from flask import Blueprint, session, render_template, request, redirect, url_for
from google.cloud import firestore
import random
from random import gauss, uniform


macro2 = Blueprint('macro2', __name__, template_folder='templates')

client = firestore.Client()

def initialize_economy():
    initial_values = {}
    initial_values['GDP'] = random.uniform(45000, 50000)
    initial_values['debt_level'] = random.uniform(20000, 30000)
    initial_values['CPI'] = 100
    initial_values['tax_rate'] = random.uniform(5, 15)
    initial_values['unemployment_rate'] = random.uniform(4, 8)
    initial_values['happiness_rate'] = random.uniform(55, 65)
    initial_values['interest_rate'] = random.uniform(3, 7)
    initial_values['tax_revenue'] = initial_values['GDP'] * (initial_values['tax_rate'] / 100.0) # Initialize tax_revenue
    initial_values['current_round'] = 1
    initial_values['public_spending_amount'] = 0
    initial_values['tax_pool'] = 0
    return initial_values

@macro2.route('/home', methods=['GET'])
def home():
    session['current_round'] = 1
    return render_template('macro2_home.html')


@macro2.route('/macro_2_start_game', methods=['GET', 'POST'])
def start_game():
    initial_values = {}  # Initialize as an empty dictionary

    # Directly fetch from session
    student_id = session.get('student_id', None)
    class_number = session.get('class_number', None)
    session.pop('economic_shock_info', None)

    if request.method == 'POST' or request.method == 'GET':
        initial_values = initialize_economy()
        initial_values['tax_pool'] = 0.0
        client.collection('macro2_game_state').document(student_id).set(initial_values)
        client.collection('macro2_game_state').document(student_id).update({'initial_values': initial_values})
    else:
        # If GET, then reset the initial values and update Firestore
        initial_values = initialize_economy()
        initial_values['tax_pool'] = 0.0
        client.collection('macro2_game_state').document(student_id).set(initial_values)

        # Store initial values as 'round_0' in Firestore
        game_state_ref = client.collection('macro2_game_state').document(student_id)
        game_state = game_state_ref.get().to_dict()
        if 'round_data' not in game_state:
            game_state['round_data'] = {}
        game_state['round_data']['round_0'] = initial_values  # Set round_0 data
        game_state_ref.update({'round_data': game_state['round_data']})

        if game_state is not None:
            initial_values = game_state
        else:
            return "Game state not found in Firestore. Please start a new game.", 400


    return render_template('macro2_start_game.html', initial_values=initial_values)

@macro2.route('/pay_interest', methods=['GET', 'POST'])
def pay_interest():
    student_id = session['student_id']
    game_state_ref = client.collection('macro2_game_state').document(student_id)
    game_state = game_state_ref.get().to_dict()
    # Save the initial state for later comparison, before any choices are made.


    session['game_state'] = game_state
    GDP = game_state['GDP']
    debt_level = game_state['debt_level']
    CPI = game_state['CPI']
    tax_rate = game_state['tax_rate']
    interest_rate = game_state['interest_rate']
    current_round = game_state['current_round']
    previous_happiness_rate = game_state['happiness_rate']
    interest = debt_level * (interest_rate / 100.0)
    nominal_GDP = GDP * (CPI / 100.0)
    tax_revenue = nominal_GDP * (tax_rate / 100.0)
    tax_pool = game_state['tax_pool'] + tax_revenue if current_round == 1 else game_state['tax_pool']

    session['initial_values_this_round'] = {
        'GDP': game_state['GDP'],
        'CPI': game_state['CPI'],
        'unemployment_rate': game_state['unemployment_rate'],
        'debt_level': game_state['debt_level'],
        'happiness_rate': game_state['happiness_rate'],
        'tax_rate': game_state['tax_rate'],
        'tax_pool': tax_pool
    }

    if request.method == 'POST':
        pay_via_tax_percentage = float(request.form['pay_via_tax'])
        max_pay_via_tax = min(tax_pool, interest)
        paid_via_tax = min(interest * (pay_via_tax_percentage / 100), max_pay_via_tax)
        paid_via_printing = interest - paid_via_tax
        pre_interest_tax_revenue = tax_revenue
        tax_pool -= paid_via_tax
        CPI *= 1 + (paid_via_printing / GDP)
        unemployment_rate = game_state['unemployment_rate']
        happiness_rate = game_state['happiness_rate']

        choices_made = game_state.get('choices_made', [])
        choice_data = {
            'round': current_round,
            'paid_via_tax': paid_via_tax,
            'paid_via_printing': paid_via_printing,
            'public_spending': 0,  # No public spending in this step
            'tax_revenue': tax_revenue,  # Current tax revenue
            'debt_level': debt_level,  # Current debt level
            'impact_on_CPI': (paid_via_printing / GDP),
            'impact_on_GDP': GDP,
            'impact_on_unemployment': unemployment_rate,
            'happiness_rate': happiness_rate,
            'interest_due': interest,  # Existing field for interest
            'pre_interest_tax_revenue': pre_interest_tax_revenue,  # <-- New field here
            'tax_revenue_available': tax_revenue,  # <-- New field to store tax revenue available for the round
            'interest_payment_to_tax_revenue': interest / tax_revenue if tax_revenue != 0 else 0,
            'tax_rate': tax_rate
        }
        choices_made.append(choice_data)

        game_state_ref.update(
            {'tax_revenue': tax_revenue, 'debt_level': debt_level, 'CPI': CPI,
             'happiness_rate': previous_happiness_rate, 'tax_pool': tax_pool,
             'choices_made': choices_made})

        return redirect(url_for('macro2.public_spending'))
    else:
        return render_template('macro2_pay_interest.html', interest_amount=interest, **locals())


@macro2.route('/public_spending', methods=['GET', 'POST'])
def public_spending():
    student_id = session['student_id']
    game_state_ref = client.collection('macro2_game_state').document(student_id)
    game_state = game_state_ref.get().to_dict()

    # Initialize latest_choice to an empty dictionary
    latest_choice = {}

    choices_made = game_state.get('choices_made', [])

    # Update latest_choice only if choices_made is not empty
    if choices_made:
        latest_choice = choices_made[-1]

    # Retrieve state variables
    GDP = game_state['GDP']
    debt_level = game_state['debt_level']
    CPI = game_state['CPI']
    unemployment_rate = game_state['unemployment_rate']
    happiness_rate = game_state['happiness_rate']
    tax_revenue = game_state['tax_revenue']
    current_round = game_state['current_round']
    diminishing_factor = 1 / (1 + 0.1 * current_round)
    tax_rate = game_state['tax_rate']
    tax_pool = game_state['tax_pool']

    if request.method == 'POST':
        # Save initial state variables for later comparison
        initial_GDP = GDP
        initial_CPI = CPI
        initial_unemployment_rate = unemployment_rate

        public_spending_amount = float(request.form.get('public_spending_amount', '0') or 0.0)
        funding_from_printing = float(request.form.get('money_printing_used', 0.0) or 0.0)
        # New lines for tax_pool_used
        tax_pool_used = float(request.form.get('tax_pool_used', 0.0) or 0.0)
        tax_pool_used = min(tax_pool_used, tax_pool)  # Ensure it doesn't exceed available tax pool

        debt_added = public_spending_amount - (funding_from_printing + tax_pool_used)  # Modified this line

        # Decide what to do with leftover funds
        leftover_action = request.form.get('leftover_action', 'pay_debt')
        leftover_to_tax_percentage = float(request.form.get('leftover_to_tax_percentage', 0.0) or 0.0) / 100
        print(f"Debug: Received leftover_to_tax_percentage value is {leftover_to_tax_percentage}")
        # Decide what to do with leftover funds
        surplus_used_for_debt = 0

        if debt_added < 0:  # Means there are leftover funds
            to_tax_pool = abs(debt_added) * (1 - leftover_to_tax_percentage)  # Flipped
            to_debt_payment = abs(debt_added) * leftover_to_tax_percentage  # Flipped
            surplus_used_for_debt = to_debt_payment  # Update the new variable

            # Debug: Log the calculated values of to_tax_pool and to_debt_payment
            print(f"Debug: Calculated to_tax_pool is {to_tax_pool}")
            print(f"Debug: Calculated to_debt_payment is {to_debt_payment}")

            tax_pool += to_tax_pool  # Add to tax pool
            debt_level -= to_debt_payment  # Pay down the debt
        else:
            debt_level += debt_added  # If no leftover, just add the debt

        # Update state variables
        tax_pool -= tax_pool_used  # Subtract the tax pool used
        CPI *= 1 + (funding_from_printing / GDP)

        # Introduce some randomness for simulation
        noise_factor_gdp = random.uniform(0.99, 1.05)
        noise_factor_unemployment = random.uniform(0.9, 1.1)

        adjustment = 1 / (
                    1 + (public_spending_amount / 100000) ** 2)  # Adjust the denominator for desired sensitivity

        # Update GDP
        GDP += (public_spending_amount * 0.6 * adjustment) * noise_factor_gdp - GDP * 0.01 * current_round

        # Update unemployment rate
        unemployment_shock = random.gauss(0.05 * unemployment_rate, 0.01 * unemployment_rate)
        unemployment_rate = max(0, (unemployment_rate - (public_spending_amount / GDP) ** 0.2 * 0.35 * diminishing_factor) * noise_factor_unemployment + unemployment_shock)

        # Calculate the changes in state variables
        change_in_GDP = GDP - initial_GDP
        change_in_CPI = CPI - initial_CPI
        change_in_unemployment = unemployment_rate - initial_unemployment_rate

        # Create a dictionary to capture this round's choices and impacts
        choice_data = {
            'round': current_round,
            'public_spending_amount': public_spending_amount,
            'public_spending': public_spending_amount,  # Add this line
            'tax_revenue': tax_revenue,  # Update this line
            'debt_level': debt_level,  # Update this line
            'tax_pool': tax_pool,  # Update this line
            'tax_pool_used': tax_pool_used,  # Add this line
            'funding_from_printing': funding_from_printing,
            'impact_on_GDP': GDP,
            'impact_on_CPI': CPI,
            'impact_on_unemployment': unemployment_rate,
            'happiness_rate': happiness_rate,
            'change_in_GDP': change_in_GDP,
            'change_in_CPI': change_in_CPI,
            'change_in_unemployment': change_in_unemployment,
            'debt_added': debt_added,
            'surplus_used_for_debt': surplus_used_for_debt,  # Add the new field
            'interest_payment_to_tax_revenue': latest_choice.get('interest_due',
                                                                 0) / tax_revenue if tax_revenue != 0 else 0,
            'tax_rate': tax_rate

        }

        # Append the data to the choices_made list
        choices_made = game_state.get('choices_made', [])
        choices_made.append(choice_data)

        # Update Firestore
        # Do not update 'happiness_rate' here
        game_state_ref.update({
            'GDP': GDP,
            'debt_level': debt_level,
            'CPI': CPI,
            'unemployment_rate': unemployment_rate,
            'tax_revenue': tax_revenue,
            'tax_pool': tax_pool,
            'current_round': current_round,
            'choices_made': choices_made  # Don't forget to update this field

        })

        return redirect(url_for('macro2.set_tax_rate'))

    else:
        choices_made = game_state.get('choices_made', [])
        latest_choice = choices_made[-1] if choices_made else None
        return render_template('macro2_public_spending.html', latest_choice=latest_choice, **game_state)

@macro2.route('/set_tax_rate', methods=['GET', 'POST'])
def set_tax_rate():
    if 'student_id' not in session:
        return "Student ID not found in session. Please login or start a new game.", 400

    student_id = session['student_id']
    game_state_ref = client.collection('macro2_game_state').document(student_id)
    game_state = game_state_ref.get().to_dict()

    if request.method == 'POST':
        # Capture user input for the new tax rate
        new_tax_rate = float(request.form['new_tax_rate'])

        # Fetch existing tax revenue
        existing_tax_pool = game_state['tax_pool']

        # Update game state variables
        game_state['tax_rate'] = new_tax_rate
        new_tax_revenue = game_state['GDP'] * (new_tax_rate / 100.0) * game_state['CPI'] / 100.0

        # Add existing tax revenue to the newly calculated one
        tax_pool = new_tax_revenue + existing_tax_pool

        # Update game state in Firestore using partial update
        game_state_ref.update({
            'tax_rate': new_tax_rate,
            'tax_pool': tax_pool
        })

        return redirect(url_for('macro2.run_election_route'))
    else:
        # Safely remove choices_made from game_state if it exists
        choices_made = game_state.pop('choices_made', [])
        return render_template('macro2_set_tax_rate.html', choices_made=choices_made, **game_state)

# Function for election logic
def run_election(happiness_rate):
    election_outcome_number = random.gauss(happiness_rate, 5)  # Gaussian distribution centered around happiness_rate
    if election_outcome_number >= 50:
        return True, election_outcome_number  # User gets re-elected
    else:
        return False, election_outcome_number  # User loses the election


@macro2.route('/run_election', methods=['GET'])
def run_election_route():
    if 'student_id' not in session:
        return 'Not logged in', 401

    student_id = session['student_id']
    game_state_ref = client.collection('macro2_game_state').document(student_id)
    game_state = game_state_ref.get().to_dict()
    current_round = game_state['current_round']
    if not game_state:
        return 'Game state not found', 404

    initial_values = game_state.get('initial_values', {})
    # Check if this is the first round
    if current_round == 1:
        initial_values_this_round = game_state.get('initial_values', {})
    else:
        # Retrieve final values from the previous round to use as initial values for this round
        previous_round_data = game_state['round_data'].get(f'round_{current_round - 1}', {})
        initial_values_this_round = {
            'GDP': previous_round_data.get('final_GDP', 0),
            'CPI': previous_round_data.get('final_CPI', 0),
            'unemployment_rate': previous_round_data.get('final_unemployment', 0),
            'debt_level': previous_round_data.get('final_debt_level', 0),
            'tax_rate': previous_round_data.get('final_tax_rate', 0),
            'tax_pool': previous_round_data.get('final_tax_pool', 0),
        }

    happiness_impact_factors = game_state.get('happiness_impact_factors', {})

    debt_to_GDP_ratio = game_state['debt_level'] / game_state['GDP']
    tax_rate_change = happiness_impact_factors.get('tax_rate_change', 0)

    # Retrieve initial values for this round
    starting_GDP = initial_values_this_round.get('GDP', 0)
    starting_CPI = initial_values_this_round.get('CPI', 0)
    starting_unemployment = initial_values_this_round.get('unemployment_rate', 0)
    starting_debt_level = initial_values_this_round.get('debt_level', 0)
    starting_tax_rate = initial_values_this_round.get('tax_rate', 0)
    starting_tax_pool = initial_values_this_round.get('tax_pool', 0)

    def calculate_change(metric):
        return game_state[metric] - initial_values_this_round.get(metric, 0)

    change_in_GDP = calculate_change('GDP')
    change_in_CPI = calculate_change('CPI')
    change_in_unemployment = calculate_change('unemployment_rate')
    change_in_debt = calculate_change('debt_level')
    change_in_debt_to_GDP = debt_to_GDP_ratio - (
                initial_values_this_round.get('debt_level', 0) / initial_values_this_round.get('GDP', 1))
    change_in_tax_rate = calculate_change('tax_rate')
    change_in_tax_pool = calculate_change('tax_pool')

    # Calculate happiness and current values
    pre_election_happiness_rate = game_state['happiness_rate']
    current_GDP = game_state['GDP']
    current_CPI = game_state['CPI']
    current_UE = game_state['unemployment_rate']
    current_tax_rate = game_state['tax_rate']
    current_tax_pool = game_state['tax_pool']

    # Store round data for later use
    round_data = {
        'starting_GDP': starting_GDP,
        'starting_CPI': starting_CPI,
        'starting_unemployment': starting_unemployment,
        'starting_debt_level': starting_debt_level,
        'starting_tax_rate': starting_tax_rate,
        'starting_tax_pool': starting_tax_pool,
        'current_GDP': current_GDP,
        'current_CPI': current_CPI,
        'current_UE': current_UE,
        'current_tax_rate': current_tax_rate,
        'current_tax_pool': current_tax_pool
    }

    debt_impact = (change_in_debt_to_GDP)*10*game_state['debt_level']/10000

    happiness_delta = (
            (0.004 + gauss(0, 0.002) + (current_round * 0.0002) + (current_GDP / 25000) * (change_in_GDP) / 1000
             - (0.02 + gauss(0, 0.005) + (current_round * 0.0004) + (
                            current_CPI / (100 / (1 + current_round / 10)))) * change_in_CPI
             - (0.2 + gauss(0, 0.05) + (current_round * 0.002) + (current_UE / 10)) * change_in_unemployment
             - (0.04 + gauss(0, 0.01) + (current_round * 0.0004)) * tax_rate_change
             - (current_tax_rate * (1 + (current_round / 20))))
            - debt_impact
    )

    happiness_rate = pre_election_happiness_rate + happiness_delta
    happiness_rate = max(0, min(100, happiness_rate))
    change_in_happiness = happiness_delta

    round_data['happiness_rate'] = happiness_rate
    # Update session['initial_values_this_round'] for the next round
    session['initial_values_this_round'] = {
        'GDP': current_GDP,
        'CPI': current_CPI,
        'unemployment_rate': current_UE,
        'debt_level': game_state['debt_level'],
        'tax_rate': current_tax_rate,
        'tax_pool': current_tax_pool,
    }

    game_state_ref.update({'happiness_rate': happiness_rate})
    round_data.update({
        'final_GDP': current_GDP,
        'final_CPI': current_CPI,
        'final_unemployment': current_UE,
        'final_happiness': happiness_rate,
        'final_tax_rate': current_tax_rate,
        'final_tax_pool': current_tax_pool,
        'final_debt_level': game_state['debt_level'],
        'final_debt_to_GDP': 100*debt_to_GDP_ratio,
        'final_interest_payment': game_state['debt_level'] * (game_state['interest_rate'] / 100.0),
        'final_interest_payment_tax_pool': 100 * game_state['debt_level'] * (
                game_state['interest_rate'] / 100.0) / current_tax_pool if current_tax_pool != 0 else 0
    })
    # Update session['initial_values_this_round'] for the next round
    session['initial_values_this_round'] = {
        'GDP': current_GDP,
        'CPI': current_CPI,
        'unemployment_rate': current_UE,
        'debt_level': game_state['debt_level'],
        'tax_rate': current_tax_rate,
        'tax_pool': current_tax_pool,
    }

    if 'round_data' not in game_state:
        game_state['round_data'] = {}

        # If this is the first round, store the initial values as 'round_0'
    if current_round == 1:
        round_0_data = game_state['round_data'].get('round_0', {})
        if not round_0_data:
            # This code assumes that initial_values is properly set and available at this point.
            round_0_data = {
                'final_GDP': initial_values['GDP'],
                'final_CPI': initial_values['CPI'],
                'final_unemployment': initial_values['unemployment_rate'],
                'final_happiness': initial_values['happiness_rate'],
                'final_tax_rate': initial_values['tax_rate'],
                'final_tax_pool': initial_values['tax_rate']*initial_values['GDP']/100,
                'final_debt_level': initial_values['debt_level'],
                'final_debt_to_GDP': 100 * initial_values['debt_level'] / initial_values['GDP'],
                'final_interest_payment': initial_values['debt_level'] * (initial_values['interest_rate'] / 100.0),
                'final_interest_payment_tax_pool': 100 * initial_values['debt_level'] * (
                        initial_values['interest_rate']) / (initial_values['tax_rate']*initial_values['GDP'])
            }
            game_state['round_data']['round_0'] = round_0_data

    game_state['round_data'][f'round_{current_round}'] = round_data
    game_state_ref.update({'round_data': game_state['round_data']})


    election_won, election_outcome_number = run_election(happiness_rate)
    election_result = "Election won, moving to next round" if election_won else "Election lost, game over"

    existing_tax_pool = game_state.get('tax_pool', 0)

    if election_won:
        game_state['current_round'] += 1
        game_state_ref.update({'current_round': game_state['current_round'],
                               'tax_revenue': game_state['tax_revenue']})
        session['current_round'] = game_state['current_round']
        update_leaderboard(student_id, session['username'], game_state['current_round'], session['class'])
    else:
        game_state['game_ended'] = True


    return render_template('macro2_run_election.html', election_result=election_result, GDP=game_state['GDP'],
                           change_in_GDP=change_in_GDP, change_in_CPI=change_in_CPI,
                           change_in_unemployment=change_in_unemployment, change_in_debt_to_GDP=change_in_debt_to_GDP,
                           change_in_debt=change_in_debt, pre_election_happiness_rate=pre_election_happiness_rate,
                           change_in_happiness=change_in_happiness, change_in_tax_pool=change_in_tax_pool, debt_level=game_state['debt_level'], change_in_tax_rate=change_in_tax_rate,
                           CPI=game_state['CPI'], unemployment_rate=game_state['unemployment_rate'],
                           happiness_rate=happiness_rate, tax_rate=game_state['tax_rate'],
                           current_round=current_round, election_outcome_number=election_outcome_number, starting_GDP=starting_GDP,
                       starting_CPI=starting_CPI,
                       starting_unemployment=starting_unemployment,
                       starting_debt_level=starting_debt_level,
                     starting_tax_pool=starting_tax_pool,
                       starting_tax_rate=starting_tax_rate, current_tax_pool=current_tax_pool)

@macro2.route('/instructions')
def instructions():
    current_username = session.get('username')
    return render_template('macro2_instructions.html', current_username=current_username)

@macro2.route('/game_results', methods=['GET'])
def game_results():
    if 'student_id' not in session:
        return 'Not logged in', 401

    student_id = session['student_id']
    game_state_ref = client.collection('macro2_game_state').document(student_id)
    game_state = game_state_ref.get().to_dict()
    if not game_state:
        return 'Game state not found', 404

    round_data = game_state.get('round_data', {})
    number_of_rounds = game_state.get('current_round', 0)
    sorted_round_data = {k: round_data[k] for k in sorted(round_data, key=lambda x: int(x.replace('round_', '')))}

    return render_template('macro2_results.html', round_data=sorted_round_data, number_of_rounds=number_of_rounds)

@macro2.route('/leaderboard', methods=['GET'])
def leaderboard():
    class_number = session.get('class')
    print("Class Number:", class_number)

    if not class_number:
        return render_template('macro2_leaderboard.html', leaderboard_by_class={})

    # Use the get_leaderboard function to fetch class-specific scores
    leaderboard_data = get_leaderboard(class_number)

    # Create a dictionary to group leaderboard data by class_number
    leaderboard_by_class = {}
    for entry in leaderboard_data:
        class_num = entry.get('class_number')
        if class_num:
            if class_num not in leaderboard_by_class:
                leaderboard_by_class[class_num] = []
            leaderboard_by_class[class_num].append(entry)

    return render_template('macro2_leaderboard.html', leaderboard_by_class=leaderboard_by_class)


def update_leaderboard(student_id, username, max_round_reached, class_number, score=None):
    # Initialize the Firestore document reference
    doc_ref = client.collection('macro2_leaderboard').document(student_id)

    # Fetch the student's current leaderboard entry
    doc = doc_ref.get()

    # Prepare the data to update
    data_to_update = {
        'student_id': student_id,
        'username': username,
        'class_number': class_number,
        'max_round_reached': max_round_reached
    }

    # If score is provided, then update the score only if it's higher than the existing one
    if score is not None:
        if not doc.exists or (doc.exists and doc.to_dict().get('max_round_reached', 0) < score):
            data_to_update['max_round_reached'] = score

    # Update the document
    doc_ref.set(data_to_update, merge=True)


def get_leaderboard(class_number):
    # Fetch all scores from Firestore
    all_scores = client.collection('macro2_leaderboard').stream()

    # Convert the data to a list of dictionaries
    all_data = [{'id': doc.id, **doc.to_dict()} for doc in all_scores]

    # Filter by class_number
    filtered_data = [entry for entry in all_data if entry.get('class_number') == class_number]

    # Group by usernames and take the maximum score for each user
    user_max_scores = {}
    for entry in filtered_data:
        username = entry['username']
        if username not in user_max_scores or entry['score'] > user_max_scores[username]['score']:
            user_max_scores[username] = entry

    leaderboard_data = sorted(user_max_scores.values(), key=lambda x: x['max_round_reached'], reverse=True)[:10]

    return leaderboard_data
