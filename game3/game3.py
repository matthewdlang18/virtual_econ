from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from google.cloud import firestore
import random

game3 = Blueprint('game3', __name__, template_folder='templates')

client = firestore.Client()

def elasticity_category(elasticity):
    if elasticity < -1:
        return "Elastic"
    elif elasticity == -1:
        return "Unitary Elastic"
    else:
        return "Inelastic"

def supply_curve(p, a, b):
    return a + b * p

def demand_curve(p, c, d):
    return c - d * p

def generate_curves():
    a = round(random.randint(-50, 10), 2)
    b = round(random.randint(1, 5), 2)
    c = round(random.randint(100, 500), 2)
    d = round(random.randint(1, 5), 2)

    p_star = round((c - a) / (b + d), 2)
    q_star = round(supply_curve(p_star, a, b), 2)
    elasticity = round(-d * (p_star / q_star), 2)

    while not (10 <= p_star <= 50) or not (50 <= q_star <= 200) or not (-1.5 <= elasticity <= -0.2):
        a = round(random.randint(-50, 10), 2)
        b = round(random.randint(1, 5), 2)
        c = round(random.randint(100, 500), 2)
        d = round(random.randint(1, 5), 2)
        p_star = round((c - a) / (b + d), 2)
        q_star = round(supply_curve(p_star, a, b), 2)
        elasticity = round(-d * (p_star / q_star), 2)

    t = round(random.uniform(0.2, 0.5) * p_star, 2)  # Tax for round 1
    a_with_tax = round(a - b * t, 2)  # Adjust supply curve for round 1 tax
    p_tax = round((c - a_with_tax) / (b + d), 2)
    q_tax = round(supply_curve(p_tax, a_with_tax, b), 2)

    t_second = round(random.uniform(0.25, 0.4) * p_tax, 2)  # Tax for round 2 based on new price after first tax
    a_with_tax_second = round(a_with_tax - b * t_second, 2)  # Adjust supply curve again for second tax
    p_tax_second = round((c - a_with_tax_second) / (b + d), 2)
    q_tax_second = round(supply_curve(p_tax_second, a_with_tax_second, b), 2)

    # Compile the results into a dictionary
    results = {
        "initial_equilibrium": {
            "price": p_star,
            "quantity": q_star,
            "elasticity_category": elasticity_category(elasticity),
            "tax": t,
        },
        "first_tax": {
            "price": p_tax,
            "quantity": q_tax,
            "tax": t_second,
        },
        "second_tax": {
            "price": p_tax_second,
            "quantity": q_tax_second,
        },
        "supply_curve": f"Qs = {a} + {b}P",
        "demand_curve": f"Qd = {c} - {d}P",
        "supply_curve_with_tax_first": f"Qs = {a_with_tax} + {b}P",
        "supply_curve_with_tax_second": f"Qs = {a_with_tax_second} + {b}P",
    }

    return results


def get_student_record(student_id, class_number, students_df):
    return students_df[(students_df['student_id'] == student_id) & (students_df['class'] == class_number)]


def calculate_high_score(total_penalty):
    return total_penalty


def get_leaderboard(class_number):
    leaderboard_ref = client.collection('leaderboard3').document(str(class_number))
    leaderboard = leaderboard_ref.get()

    if leaderboard.exists:
        students = leaderboard.to_dict().get('students', [])
        # Sorting the students by penalty in ascending order (lowest penalty first)
        students.sort(key=lambda x: x['penalty'])
        return students
    else:
        return []


def update_leaderboard(student_id, class_number, username, total_penalty):
    leaderboard_ref = client.collection('leaderboard3').document(str(class_number))
    leaderboard = leaderboard_ref.get()

    # Check if the document exists
    if leaderboard.exists:
        students = leaderboard.to_dict().get('students', [])
    else:
        students = []

    # Check if the student is already in the leaderboard
    student_found = False
    for student in students:
        if student['student_id'] == student_id:
            # Only update the penalty if the new penalty is lower (better)
            if total_penalty < student['penalty']:
                student['penalty'] = total_penalty
            student_found = True
            break

    if not student_found:
        students.append({
            'student_id': student_id,
            'username': username,
            'penalty': total_penalty
        })

    # Sorting the students by penalty in ascending order (lowest penalty first)
    students.sort(key=lambda x: x['penalty'])

    # Update or create the document
    leaderboard_ref.set({'students': students})


@game3.route('/home3')
def home3():
    return render_template('home3.html')

@game3.route('/game3', methods=['GET', 'POST'])
def play_game3_round1():
    if 'username' in session:
        results = generate_curves()
        session['results'] = results
    else:
        # If username is not in the session, redirect to the home page or some login page
        return redirect(url_for('game3.home3'))

    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('game3.play_game3_round1'))

    # Separate the rendering of the template based on whether results exist
    if results is not None:
        return render_template('game3_round1.html', supply_equation=results['supply_curve'], demand_equation=results['demand_curve'], results=results)
    else:
        # Clear the session and render the template without results
        session.clear()
        return render_template('game3_round1.html')


@game3.route('/round1', methods=['POST'])
def feedback1():
    guess1 = float(request.form['guess_price'])
    results = session.get('results')
    true_equilibrium_price_after_tax = results['first_tax']['price']  # After-tax price
    equilibrium_quantity_after_tax = results['first_tax']['quantity']  # Add this line
    difference1 = round(guess1 - true_equilibrium_price_after_tax, 2)
    session['difference1'] = round(difference1, 2)
    session['guess_round1'] = guess1

    threshold_value = 0.01  # You can define the threshold value as per your logic

    return render_template('game3_feedback.html', round_number=1, guess=guess1,
                           true_equilibrium_price=true_equilibrium_price_after_tax,
                            equilibrium_quantity=equilibrium_quantity_after_tax,
                           difference=session['difference1'], threshold=threshold_value,
                           guess_round2=session.get('guess_round2', None))


@game3.route('/game3_proceed1', methods=['POST'])
def game3_proceed1():
    results = session.get('results')
    original_price = results['initial_equilibrium']['price']
    original_quantity = results['initial_equilibrium']['quantity']
    previous_price = results['first_tax']['price']
    tax = results['initial_equilibrium']['tax']
    elasticity = results['initial_equilibrium']['elasticity_category']
    supply_equation = results['supply_curve_with_tax_first']

    threshold_value = 0.01  # You can define the threshold value as per your logic

    # Store the results dictionary back in the session
    session['results'] = results

    return render_template('game3_round2.html', original_price=original_price, original_quantity=original_quantity,
                           previous_price=previous_price, tax=tax, elasticity=elasticity,
                           supply_equation=supply_equation, threshold=threshold_value, results=results)

@game3.route('/round2', methods=['POST'])
def feedback2():
    guess2 = float(request.form['guess_price'])
    results = session.get('results')
    new_equilibrium_price = results['second_tax']['price']  # Price after the second tax
    new_equilibrium_quantity = results['second_tax']['quantity']
    difference2 = round(guess2 - new_equilibrium_price, 2)
    session['difference2'] = round(difference2, 2)
    session['guess_round2'] = guess2

    threshold_value = 0.01  # You can define the threshold value as per your logic

    return render_template('game3_feedback2.html', guess=guess2,
                           true_equilibrium_price=new_equilibrium_price,
                            equilibrium_quantity=new_equilibrium_quantity,
                           difference=difference2, threshold=threshold_value,
                           guess_round1=session.get('guess_round1', None))


@game3.route('/game3_proceed2', methods=['POST'])
def game3_proceed2():
    results = session.get('results')
    previous_price = results['first_tax']['price']  # Price after the first tax
    previous_quantity = results['first_tax']['quantity']
    tax = results['first_tax']['tax']  # Second tax applied
    elasticity = results['initial_equilibrium']['elasticity_category']
    supply_equation = results['supply_curve_with_tax_second']  # Updated supply curve

    threshold_value = 0.01  # You can define the threshold value as per your logic

    return render_template('game3_round2.html', previous_price=previous_price, tax=tax, previous_quantity=previous_quantity,
                           elasticity=elasticity, supply_equation=supply_equation, threshold=threshold_value)

# ... (import statements and blueprint definition) ...
@game3.route('/game3_results', methods=['POST'])
def game3_results():
    results = session.get('results')
    rounds_data = []
    total_penalty = 0.0

    # Iterate through the 2 rounds
    for i in range(2):
        guess_key = f'guess_round{i + 1}'
        if guess_key in session:
            submitted_price = session[guess_key]
            actual_price = results['first_tax']['price'] if i == 0 else results['second_tax']['price']
            difference = abs(submitted_price - actual_price)
            penalty_multiplier = 2 if submitted_price > actual_price else 1
            penalty = round(penalty_multiplier * difference, 2)
            total_penalty += penalty
            status = "Right amount" if difference == 0 else "Too high" if submitted_price > actual_price else "Too low"
            rounds_data.append({
                'round_number': i + 1,
                'difference': round(difference, 2),
                'tax': round(results['initial_equilibrium']['tax'] if i == 0 else results['first_tax']['tax'], 2),
                'guess': round(session.get(guess_key, None), 2),
                'status': status,
                'penalty': penalty
            })
        else:
            print(f"Warning: {guess_key} not found in session!")  # Debugging print statement
            continue  # Skip to the next iteration if the guess is not found

    # Update the leaderboard with the student's high score
    student_id = session['student_id']
    class_number = session['class']
    current_username = session['username']
    high_score = calculate_high_score(total_penalty)
    update_leaderboard(student_id, class_number, current_username, high_score)

    return render_template('game3_results.html', results=results, total_penalty=round(total_penalty, 2),
                           rounds_data=rounds_data, username=session.get('username'))


@game3.route('/start_over3')
def start_over3():
    # Store the username before clearing the keys
    username_to_keep = session.get('username')

    keys_to_clear = ['results', 'difference1', 'difference2', 'username']
    for key in keys_to_clear:
        session.pop(key, None)

    # Add the username back to the session
    if username_to_keep:
        session['username'] = username_to_keep

    return redirect(url_for('game3.play_game3_round1'))



@game3.route('/leaderboard/<int:class_number>')
def leaderboard(class_number):
    students = get_leaderboard(class_number)
    return render_template('game3_leaderboard.html', class_number=class_number, students=students)

@game3.route('/instructions')
def instructions():
    current_username = session.get('username')
    return render_template('game3_instructions.html', current_username=current_username)

