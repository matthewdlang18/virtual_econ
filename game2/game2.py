from flask import Flask, Blueprint, render_template, request, session, redirect, url_for, make_response, send_file
from sympy import symbols, Eq, solve, N
from flask import jsonify
import random
import pandas as pd
from google.cloud import firestore

game2 = Blueprint('game2', __name__, template_folder='templates')

client = firestore.Client()
P = symbols('P')
MAX_ITERATIONS = 1000


def generate_equations():
    iterations = 0
    while True:  # Keep looping until valid numbers are found
        iterations += 1
        a = random.randint(-20, 20)  # Adjusted range
        b = random.randint(1, 5)  # Adjusted range
        c = random.randint(50, 100)  # Adjusted range
        d = random.randint(1, 5)  # Adjusted range

        # Supply and Demand equations
        supply_eq = a + b * P
        demand_eq = c - d * P

        # Equilibrium price by setting supply equal to demand
        equilibrium_price_solution = solve(Eq(supply_eq, demand_eq), P)[0]

        # Equilibrium quantity using the supply equation
        equilibrium_quantity = supply_eq.subs(P, equilibrium_price_solution)
        equilibrium_quantity_float = float(equilibrium_quantity)

        # Check if price and quantity are positive
        if equilibrium_price_solution > 0 and equilibrium_quantity_float > 0:
            break

        # Fallback strategy if too many iterations
        if iterations >= MAX_ITERATIONS:
            a, b, c, d = 10, 2, 30, 3  # Fallback values
            equilibrium_quantity_float = 10.0  # Fallback value
            break

    return a, b, c, d, f"{a} + {b}P", f"{c} - {d}P", round(equilibrium_quantity_float, 2)


def apply_shock(a, b, c, d, shock, size_label):
    # Define the shock ranges for small, medium, and large
    shock_ranges = {
        "small": (1, 5),
        "medium": (6, 10),
        "large": (11, 20)
    }

    # Get the corresponding shock range based on the size label
    shock_range = shock_ranges[size_label]
    shock_size = random.randint(*shock_range)

    # Define the effect of shocks on demand (modifying c) and supply (modifying a)
    demand_shifts = {
        "consumer incomes increase": shock_size,
        "consumer incomes decrease": -shock_size,
        "price of a complement increases": -shock_size,
        "price of a complement decreases": shock_size,
        "price of a substitute increases": shock_size,
        "price of a substitute decreases": -shock_size,
        "population increases": shock_size,
        "population decreases": -shock_size
    }

    supply_shifts = {
        "price of inputs increases": -shock_size,
        "price of inputs decreases": shock_size,
        "better technology is created for production": shock_size,
        "firms enter the market": shock_size,
        "firms leave the market": -shock_size
    }

    # Apply the shock to the constants
    if shock in demand_shifts:
        c += demand_shifts[shock]
    elif shock in supply_shifts:
        a += supply_shifts[shock]

    # Recalculate the supply and demand equations
    supply_eq = a + b * P
    demand_eq = c - d * P
    equilibrium_price_solution = solve(Eq(supply_eq, demand_eq), P)[0]
    equilibrium_quantity = supply_eq.subs(P, equilibrium_price_solution)
    equilibrium_quantity_float = float(equilibrium_quantity)

    # Check if price and quantity are positive, if not, adjust the shock
    while equilibrium_price_solution <= 0 or equilibrium_quantity_float <= 0:
        # You can regenerate or modify the shock here
        # For simplicity, let's just regenerate the shock size
        shock_size = random.randint(*shock_range)
        if shock in demand_shifts:
            c += shock_size  # Adjusting the demand shock
        elif shock in supply_shifts:
            a += shock_size  # Adjusting the supply shock
        equilibrium_price_solution = solve(Eq(supply_eq, demand_eq), P)[0]
        equilibrium_quantity = supply_eq.subs(P, equilibrium_price_solution)
        equilibrium_quantity_float = float(equilibrium_quantity)

    if equilibrium_quantity_float is not None:
        equilibrium_quantity_float = round(equilibrium_quantity_float, 2)  # Round to 2 decimal places

    # Save the shock details
    shock_details = {
        "shock": shock,
        "size": shock_size,
        "affected": "demand" if shock in demand_shifts else "supply"
    }
    return a, b, c, d, equilibrium_quantity_float, shock_details  # Add shock_details to the return values


def get_student_record(student_id, class_number, students_df):
    return students_df[(students_df['student_id'] == student_id) & (students_df['class'] == class_number)]


def calculate_high_score(total_penalty):
    return total_penalty


def get_leaderboard(class_number):
    leaderboard_ref = client.collection('leaderboard2').document(str(class_number))
    leaderboard = leaderboard_ref.get()

    if leaderboard.exists:
        students = leaderboard.to_dict().get('students', [])
        # Sorting the students by penalty in ascending order (lowest penalty first)
        students.sort(key=lambda x: x['penalty'])
        return students
    else:
        return []


def update_leaderboard(student_id, class_number, username, total_penalty):
    leaderboard_ref = client.collection('leaderboard2').document(str(class_number))
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


@game2.route('/home2')
def home2():
    return render_template('home2.html')


@game2.route('/game2', methods=['GET', 'POST'])
def play_game2_round1():
    if 'username' in session:
        # Username already in session, start a new game
        a, b, c, d, supply_equation, demand_equation, equilibrium_quantity = generate_equations()
        session['a'], session['b'], session['c'], session['d'] = a, b, c, d
        session['supply_equation1'] = supply_equation
        session['demand_equation1'] = demand_equation
        session['true_equilibrium_quantity'] = equilibrium_quantity
        return render_template('game2_round1.html', supply_equation=supply_equation, demand_equation=demand_equation)

    # Handle the username input form
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('username'))

    session.clear()
    return render_template('game2_round1.html')


@game2.route('/round1', methods=['POST'])
def feedback1():
    print("Inside feedback1 route")
    true_equilibrium_quantity = session.get('true_equilibrium_quantity', None)
    print("Retrieving true_equilibrium_quantity:", true_equilibrium_quantity)
    if true_equilibrium_quantity is None:
        return redirect(url_for('username'))
    guess1 = float(request.form['equilibrium_quantity'])
    session['guess1'] = guess1  # Make sure to store the guess in the session
    print("Stored guess1 in session:", guess1)  # Debugging print statement
    difference1 = abs(guess1 - true_equilibrium_quantity)
    session['difference1'] = round(difference1, 2)
    return render_template('game2_feedback.html', round_number=1, guess=guess1,
                           true_equilibrium_quantity=true_equilibrium_quantity,
                           difference=session['difference1'])


@game2.route('/game2_proceed1', methods=['POST'])
def game2_proceed1():
    # Retrieving the constants from the session
    a, b, c, d = session['a'], session['b'], session['c'], session['d']

    session['shock'] = random.choice([
        "consumer incomes increase",
        "consumer incomes decrease",
        "price of a complement increases",
        "price of a complement decreases",
        "price of a substitute increases",
        "price of a substitute decreases",
        "population increases",
        "population decreases",
        "price of inputs increases",
        "price of inputs decreases",
        "better technology is created for production",
        "firms enter the market",
        "firms leave the market",
    ])
    session['size'] = random.choice(["small", "medium", "large"])
    session['demand_size'] = random.choice(["small", "medium", "large"])
    session['supply_size'] = random.choice(["small", "medium", "large"])
    session['supply_equation2'] = f"{a} + {b}P"
    session['demand_equation2'] = f"{c} - {d}P"
    previous_q = session['true_equilibrium_quantity']  # Get the actual equilibrium quantity from round 1
    return render_template('game2_round2.html', shock=session['shock'], size=session['size'], previous_q=previous_q)


@game2.route('/round2', methods=['POST'])
def feedback2():
    guess2 = float(request.form['equilibrium_quantity'])
    a, b, c, d = session['a'], session['b'], session['c'], session['d']
    size_label = session['size']

    # Apply the shock and get the modified constants and equilibrium quantity
    a, b, c, d, equilibrium_quantity_with_shock, shock_details = apply_shock(a, b, c, d, session['shock'], size_label)

    # Store the updated constants and equilibrium quantity in the session
    supply_equation = f"{a} + {b}P"
    demand_equation = f"{c} - {d}P"
    session['supply_equation2'] = supply_equation
    session['demand_equation2'] = demand_equation
    session['a'], session['b'], session['c'], session['d'] = a, b, c, d
    session['equilibrium_quantity_with_shock'] = equilibrium_quantity_with_shock
    session['guess2'] = guess2
    session['shock_details_round2'] = shock_details

    difference2 = abs(guess2 - equilibrium_quantity_with_shock)
    session['difference2'] = round(difference2, 2)
    return render_template('game2_feedback.html', round_number=2, guess=guess2,
                           true_equilibrium_quantity=equilibrium_quantity_with_shock,
                           difference=session['difference2'])


@game2.route('/game2_proceed2', methods=['POST'])
def game2_proceed2():
    # Randomly select demand and supply shocks
    session['demand_shift'] = random.choice([
        "consumer incomes increase",
        "consumer incomes decrease",
        "price of a complement increases",
        "price of a complement decreases",
        "price of a substitute increases",
        "price of a substitute decreases",
        "population increases",
        "population decreases",
    ])
    session['supply_shift'] = random.choice([
        "price of inputs increases",
        "price of inputs decreases",
        "better technology is created for production",
        "firms enter the market",
        "firms leave the market",
    ])
    session['size'] = random.choice(["small", "medium", "large"])
    previous_q = session['equilibrium_quantity_with_shock']
    return render_template('game2_round3.html', demand_shift=session['demand_shift'],
                           supply_shift=session['supply_shift'], demand_size=session['demand_size'],
                           supply_size=session['supply_size'], previous_q=previous_q)


@game2.route('/game2_round3', methods=['GET', 'POST'])
def feedback3():
    print("Entering feedback3")  # Debugging line
    a = session['a']
    b = session['b']
    c = session['c']
    d = session['d']
    equilibrium_quantity_with_shock = session['equilibrium_quantity_with_shock']

    if request.method == 'POST':
        guess3 = float(request.form['equilibrium_quantity'])

        # Assuming you now have two separate size labels stored in the session
        demand_size_label = session['demand_size']
        supply_size_label = session['supply_size']

        # Apply the demand shock with its own size label
        a, b, c, d, equilibrium_quantity_with_shifts, shock_details = apply_shock(a, b, c, d, session['demand_shift'],
                                                                                  demand_size_label)
        session['shock_details_round3_demand'] = shock_details

        # Apply the supply shock with its own size label
        a, b, c, d, equilibrium_quantity_with_shifts, shock_details = apply_shock(a, b, c, d, session['supply_shift'],
                                                                                  supply_size_label)
        session['shock_details_round3_supply'] = shock_details

        # Debugging lines to print the variables
        print("a:", a, "b:", b, "c:", c, "d:", d)
        print("equilibrium_quantity_with_shifts:", equilibrium_quantity_with_shifts)

        # Update the supply and demand equations for round 3
        supply_equation = f"{a} + {b}P"
        demand_equation = f"{c} - {d}P"
        session['supply_equation3'] = supply_equation
        session['demand_equation3'] = demand_equation
        session['true_equilibrium_quantity_with_shifts'] = equilibrium_quantity_with_shifts
        session['guess3'] = guess3

        difference3 = abs(guess3 - equilibrium_quantity_with_shifts)
        session['difference3'] = round(difference3, 2)
        return render_template('game2_feedback.html', round_number=3, guess=guess3,
                               true_equilibrium_quantity=equilibrium_quantity_with_shifts,
                               difference=session['difference3'],
                               demand_size=session['demand_size'],
                               supply_size=session['supply_size'])

    # If the method is GET, render the round3.html template for the user to submit the guess
    return render_template('game2_round3.html', )


@game2.route('/game2_results', methods=['POST'])
def game2_results():
    # Check if the results have already been processed
    if session.get('results_processed'):
        return render_template('game2_results.html', current_username=session['current_username'],
                               total_penalty=session['total_penalty'],
                               rounds_data=session['rounds_data'])

    current_username = session.get('username')
    rounds_data = []
    total_penalty = 0.0  # Sum of penalties

    # Iterate through the 3 rounds
    for i in range(3):
        guess_key = f'guess{i + 1}'
        if guess_key in session:
            submitted_q = session[guess_key]
            actual_q = session[f'true_equilibrium_quantity'] if i == 0 else session[
                f'equilibrium_quantity_with_shock'] if i == 1 else session[f'true_equilibrium_quantity_with_shifts']
            difference = abs(submitted_q - actual_q)
            penalty_multiplier = 2 if submitted_q > actual_q else 1
            penalty = round(penalty_multiplier * difference, 2)  # Round to 2 decimal places
            total_penalty += round(penalty, 2)
            status = "Right amount" if difference == 0 else "Too much" if submitted_q > actual_q else "Too little"
            rounds_data.append({
                'username': current_username,
                'supply_equation': session[f'supply_equation{i + 1}'],
                'demand_equation': session[f'demand_equation{i + 1}'],
                'actual_q': actual_q,
                'submitted_q': submitted_q,
                'difference': round(difference, 2),  # Round to 2 decimal places
                'status': status,
                'penalty': penalty
            })
        else:
            print(f"Warning: {guess_key} not found in session!")  # Debugging print statement
            continue  # Skip to the next iteration if the guess is not found

    shifts = [
        {"round": 2, "type": session['shock_details_round2']['affected'],
         "description": session['shock_details_round2']['shock']},
        {"round": 3, "type": "demand", "description": session['shock_details_round3_demand']['shock']},
        {"round": 3, "type": "supply", "description": session['shock_details_round3_supply']['shock']}
    ]

    # Calculate the high score based on the total penalty
    high_score = calculate_high_score(total_penalty)

    # Update the leaderboard with the student's high score
    # Assuming student_id and class_number are available in the session
    student_id = session['student_id']
    class_number = session['class']
    session['class'] = class_number
    update_leaderboard(student_id, class_number, current_username, high_score)

    return render_template('game2_results.html', current_username=current_username,
                           total_penalty=round(total_penalty, 2),
                           rounds_data=rounds_data, shifts=shifts)


@game2.route('/start_over')
def start_over():
    # List of keys related to the game
    keys_to_clear = [
        'a', 'b', 'c', 'd',
        'supply_equation1', 'demand_equation1',
        'true_equilibrium_quantity',
        'guess1', 'difference1',
        'shock', 'size', 'supply_equation2', 'demand_equation2',
        'equilibrium_quantity_with_shock', 'guess2', 'difference2',
        'demand_shift', 'supply_shift', 'supply_equation3', 'demand_equation3',
        'true_equilibrium_quantity_with_shifts', 'guess3', 'difference3',
        'results_processed',  # Clear the results_processed flag
        # Add any other keys related to the game that you want to clear
    ]

    # Clear the specified keys
    for key in keys_to_clear:
        session.pop(key, None)

    return redirect(url_for('game2.play_game2_round1'))


@game2.route('/process_results', methods=['POST'])
def process_results():
    # Retrieve data from the session
    username = session['username']
    rounds_data = session['rounds_data']
    total_penalty = session['total_penalty']

    # Get the strategy answer submitted by the student
    strategy_answer = request.form.get('strategy_answer')

    # Optional: Save the strategy answer to the database or session
    # ...
    shifts = [
        {"round": 2, "type": "demand", "description": session['shock_details_round2']['shock']},
        {"round": 3, "type": "demand", "description": session['shock_details_round3_demand']['shock']},
        {"round": 3, "type": "supply", "description": session['shock_details_round3_supply']['shock']}
    ]

    # Clear the existing rounds_data from the session
    session.pop('rounds_data', None)


@game2.route('/leaderboard/<int:class_number>')
def leaderboard(class_number):
    students = get_leaderboard(class_number)
    return render_template('game2_leaderboard.html', class_number=class_number, students=students)


@game2.route('/instructions')
def instructions2():
    current_username = session.get('username')
    return render_template('game2_instructions.html', current_username=current_username)