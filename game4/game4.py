from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash
from google.cloud import firestore
from random import choice
import random
import math
import pandas as pd

game4 = Blueprint('game4', __name__, template_folder='templates')

client = firestore.Client()



def generate_random_number(P_prime):
    lower_range = (0.25 * P_prime, P_prime * 0.5)
    upper_range = (P_prime * 1.5, 1.75 * P_prime)

    if random.choice([True, False]):
        return random.uniform(*lower_range)
    else:
        return random.uniform(*upper_range)


@game4.route('/home4')
def home4():
    # Resetting only the game-related session data, preserving the username and other login info
    game_related_keys = ['round_number', 'tokens', 'profit1', 'a', 'b', 'f', 'q_prime', 'P_prime', 'P1', 'guessed_prices', 'game_details']
    for key in game_related_keys:
        if key in session:
            del session[key]
    return render_template('home4.html')


@game4.route('/game4', methods=['GET', 'POST'])
def play_game4():
    print("Entered play_game4 route.")  # Added log

    if 'username' not in session:
        print("Username not found in session. Redirecting to home4.")  # Added log
        return redirect(url_for('game4.home4'))

    if request.method == 'GET':
        a = random.randint(100, 300) * 10
        b = random.randint(1, 5)

        f = random.randint(5, 40) * 10
        q_prime = round(math.sqrt(2 * f), 2)
        P_prime = round(q_prime, 2)
        P1 = round(generate_random_number(P_prime), 2)

        students_df = fetch_student_data()

        session['a'] = a
        session['b'] = b
        session['f'] = f
        session['q_prime'] = q_prime
        session['P_prime'] = P_prime
        session['P1'] = P1
        session['adjustment1'] = "profit"  # Setting the adjustment for the first round to profit

        return render_template('game4_start_game.html', a=a, b=b, f=f, P1=P1)

    else:
        enter_market1 = request.form.get('enter_market1')
        q1 = float(request.form.get('quantity'))

        f = session['f']
        P1 = session['P1']
        P_prime = session['P_prime']

        ATC = f / P1 + 0.5 * P1
        ATC = round(ATC, 2)
        profit1 = round((P1 - ATC) * P1,2)
        session['profit1'] = profit1

        if P1 < P_prime:
            if enter_market1.lower() == 'n':
                message = "You made the correct choice by staying out of the market. You earned 10 tokens."
                correct1 = 1
            else:
                message = "You made the incorrect choice by entering the market."
                correct1 = 0
        else:
            if enter_market1.lower() == 'n':
                message = "You made the incorrect choice by staying out of the market."
                correct1 = 0
            else:
                message = "You made the correct choice by entering the market. You earned 10 tokens."
                correct1 = 1

        if round(q1, 2) == round(P1, 2):
            message += " You earned 10 tokens for choosing the correct quantity"
            correct2 = 1
        else:
            if enter_market1.lower() == 'y':
                message += " You did not choose the correct quantity"
            else:
                message += " Your hypothetical quantity choice was not correct"
            correct2 = 0

        tokens = 0
        if correct1 == 1:
            tokens += 10
        if correct2 == 1:
            tokens += 10


        session['tokens'] = tokens
        session['message'] = message
        session['profit1'] = profit1
        session['P1'] = P1
        session['P_prime'] = P_prime
        session['q1'] = q1

        students_df = fetch_student_data()

        guessed_prices = session.get('guessed_prices', [])
        actual_prices = session.get('actual_prices', [])

        guessed_prices.append(q1)
        actual_prices.append(P1)

        session['guessed_prices'] = guessed_prices
        session['actual_prices'] = actual_prices

        return redirect(url_for('game4.game4_token_results'))

    session['round_number'] = 0

    return redirect(url_for('game4.game4_token_results'))

@game4.route('/game4_token_results')
def game4_token_results():
    tokens = session.get('tokens', 0)
    message = session.get('message', '')

    # Check if tokens are zero or less
    restart_game = False
    if tokens <= 0:
        restart_game = True
        message += " You do not have any tokens. You must start over."

    return render_template('game4_token_results.html', tokens=tokens, message=message, restart_game=restart_game)

@game4.route('/game_round', methods=['GET', 'POST'])
def play_game_round():
    round_number = session.get('round_number', 1)
    tokens = session.get('tokens', 0)
    P1 = session.get(f'P{round_number}', 0)
    P_prime = session.get('P_prime', 0)
    q1 = float(request.form.get('guessed_price', 0))  # Initialize q1 here

    # Retrieve the previous guessed price from the session.
    previous_guessed_price = session.get(f'guessed_price{round_number - 1}', None)


    # Calculate the difference if there's a previous guessed price and a previous market price
    if previous_guessed_price is not None and session.get(f'P{round_number - 1}', None) is not None:
        price_difference_prev_round = abs(session.get(f'P{round_number - 1}') - previous_guessed_price)
    else:
        price_difference_prev_round = None

    if request.method == 'POST':
        if not q1:  # If q1 is 0, it means guessed_price_value was missing or invalid
            flash('Please enter a guess for the price.', 'error')
            return redirect(url_for('game4.play_game_round'))

    profit = session.get(f'profit{round_number}', 0)
    prev_price = session.get(f'P{round_number}', 0)
    f = session['f']
    session['optimal_price'] = session.get('P_prime', 0)

    if request.method == 'GET':
        adjustment = session.get(f'adjustment{round_number}', 'none')
        return render_template('game4_play_round.html', profit=profit, prev_price=prev_price, tokens=tokens,
                               adjustment=adjustment, round_number=round_number,
                               previous_guessed_price=previous_guessed_price,
                               price_difference_prev_round=price_difference_prev_round)
    else:
        guessed_price_value = request.form.get('guessed_price')

        # Apply the adjustment for this round to determine the new price
        adjustment = session.get(f'adjustment{round_number}', 'none')
        if adjustment == "profit":
            if profit > 0:  # positive profit
                new_price = round(prev_price - ((prev_price - P_prime) * random.uniform(0.5, 1.1)), 2)
            else:  # negative or zero profit
                new_price = round(prev_price + ((P_prime - prev_price) * random.uniform(0.5, 1.1)), 2)
        elif adjustment in ["demand_increase", "demand_decrease"]:
            # Determine if the shock should be large or small
            shock_type = choice(['large', 'small'])

            if adjustment == "demand_increase":
                if shock_type == 'large':
                    demand_shock = random.uniform(1.65, 1.9)
                else:
                    demand_shock = random.uniform(1.1, 1.45)
            else:  # demand_decrease
                if shock_type == 'large':
                    demand_shock = random.uniform(0.1, 0.45)
                else:
                    demand_shock = random.uniform(0.65, 0.9)

            new_price = round(prev_price * demand_shock, 2)
        else:
            new_price = prev_price

        guessed_price = float(guessed_price_value)
        session[f'guessed_price{round_number}'] = guessed_price
        price_difference = abs(new_price - guessed_price)
        session[f'price_difference{round_number}'] = price_difference
        tokens -= round(price_difference, 2)

        # bonus token for being within 25 cents
        if price_difference <= 0.25:
            tokens += round(1, 1)
            flash('Congratulations! You were within 25 cents of the market price and earned an extra token!', 'success')

        # bonus 5 tokens for being exactly correct
        if price_difference < 0.02:
            tokens += round(5, 1)
            flash('Amazing! Your guess was within 0.01 of the market price! Here are 5 extra tokens!', 'success')

        # Determine the adjustment for the next round
        next_round_number = round_number + 1
        if next_round_number % 2 == 1:  # odd rounds
            session[f'adjustment{next_round_number}'] = "profit"
        else:  # even rounds
            demand_shock = random.choice([0.8, 1.2])
            next_adjustment = "demand_increase" if demand_shock > 1 else "demand_decrease"
            session[f'adjustment{next_round_number}'] = next_adjustment

        game_details = session.get('game_details', [])
        if round_number > 1:
            game_details[-1]['market_price'] = P1  # Shifting the previous round's market price
        game_details.append({
            'round_number': round_number,
            'adjustment': adjustment,
            'market_price': None,  # Initialize as None; will be filled in next round
            'guessed_price': q1,
            'optimal_price': P_prime,
            'tokens': tokens
        })
        session['game_details'] = game_details

        session['tokens'] = round(tokens, 2)
        session['round_number'] = round_number + 1
        session[f'P{round_number + 1}'] = new_price
        session[f'profit{round_number + 1}'] = (new_price - ((f / new_price) + (0.5 * new_price))) * new_price
        session['optimal_price'] = P_prime
        session['f'] = f

    if tokens <= 0:
        student_id = session['student_id']
        class_number = session['class']
        username = session['username']

        # Update the leaderboard only if necessary.
        update_leaderboard_score(student_id, class_number, username, round_number)

        game_details[-1]['market_price'] = new_price

        return render_template('game4_final_results.html', game_details=game_details, rounds=round_number,
                               tokens=tokens, optimal_price=P_prime, f=f)

    return redirect(url_for('game4.play_game_round'))

@game4.route('/game4_final_results')
def game4_final_results():
    initial_tokens = session.get('initial_tokens', 0)  # Retrieve starting_tokens from session

    round_number = session.get('round_number', 1)
    student_id = session['student_id']

    print("Entering game4_final_results route.")  # Added log
    guessed_prices = session['guessed_prices']
    actual_prices = session['actual_prices']
    shocks = [session.get(f'adjustment{i}', 'none') for i in range(1, round_number+1)]
    differences = [abs(guess - actual) for guess, actual in zip(guessed_prices, actual_prices)]
    game_details = session.get('game_details', [])

    tokens = session.get('tokens', 0)
    round_number = session.get('round_number', 1)
    student_id = session['student_id']
    optimal_price = session.get('P_prime', 0)
    f = session.get('f', 0)

    return render_template('game4_final_results.html', guessed_prices=guessed_prices, actual_prices=actual_prices,
                           shocks=shocks, differences=differences, game_details=game_details, rounds=round_number,
                           tokens=tokens, initial_tokens=initial_tokens, optimal_price=optimal_price)

def update_leaderboard_score(student_id, class_number, username, new_score):
    leaderboard_ref = client.collection('leaderboard4')

    # Query for the specific student's record
    query = leaderboard_ref.where('student_id', '==', student_id).where('class', '==', class_number)
    records = query.stream()
    existing_record = [doc for doc in records]

    # If record exists and new score is greater than existing score, update.
    if existing_record:
        existing_data = existing_record[0].to_dict()
        existing_high_score = existing_data.get('score', 0)

        if new_score > existing_high_score:
            existing_record[0].reference.update({'score': new_score, 'username': username})
    else:
        # If the record doesn't exist, create a new one.
        leaderboard_data = {
            'student_id': student_id,
            'class': class_number,
            'username': username,
            'score': new_score
        }
        leaderboard_ref.add(leaderboard_data)

    print("Leaderboard updated.")


def read_leaderboard(class_number=None):
    leaderboard_ref = client.collection('leaderboard4')  # Updated collection name

    # If class_number is specified, filter the results by class
    if class_number is not None:
        results = leaderboard_ref.where('class', '==', class_number).stream()
    else:
        results = leaderboard_ref.stream()

    leaderboard_data = [doc.to_dict() for doc in results]
    df = pd.DataFrame(leaderboard_data)

    print("Leaderboard DataFrame:")
    print(df.head())  # Print the first few rows
    return df


def write_leaderboard(leaderboard_df):
    leaderboard_ref = client.collection('leaderboard4')  # Updated collection name

    # Start a batch
    batch = client.batch()

    # Delete existing documents
    for doc in leaderboard_ref.stream():
        batch.delete(doc.reference)

    # Add updated records
    for index, row in leaderboard_df.iterrows():
        leaderboard_data = {
            'student_id': row['student_id'],
            'class': row['class'],
            'username': row['username'],
            'high_score': row['high_score']
        }
        batch.add(leaderboard_ref.document(), leaderboard_data)

    # Commit the batch
    batch.commit()

    print("Leaderboard updated in Firestore.")





def get_student_record(student_id, class_number):
    students_df = fetch_student_data()
    return students_df[(students_df['student_id'] == student_id) & (students_df['class'] == class_number)]

def add_student_score(student_id, class_number, username, rounds):
    update_leaderboard_score(student_id, class_number, username, rounds)

def fetch_student_data():
    students_ref = client.collection('students')  # Adjust the collection name as needed
    student_data = [doc.to_dict() for doc in students_ref.stream()]
    return pd.DataFrame(student_data)

def calculate_high_score(student_id, class_number):
    student_record = get_student_record(student_id, class_number)
    if student_record.empty:
        return 0
    else:
        return student_record['rounds'].max()


@game4.route('/leaderboard/<int:class_number>', methods=['GET'])
def leaderboard4(class_number):
    leaderboard_ref = client.collection('leaderboard4')
    results = leaderboard_ref.where('class', '==', class_number).order_by('score',
                                                                          direction=firestore.Query.DESCENDING).limit(
        20).stream()

    leaderboard_data = [doc.to_dict() for doc in results]
    print(leaderboard_data)
    return render_template("game4_leaderboard.html", scores=leaderboard_data, class_number=class_number)

@game4.route('/instructions')
def instructions():
    current_username = session.get('username')
    return render_template('game4_instructions.html', current_username=current_username)
