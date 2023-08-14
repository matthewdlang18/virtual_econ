from flask import Blueprint, render_template, request, session, jsonify
import random
import math
from google.cloud import firestore
import pandas as pd
from pandas import to_numeric

game1 = Blueprint('game1', __name__, template_folder='templates')

client = firestore.Client()

def read_leaderboard(class_number=None):
    leaderboard_ref = client.collection('leaderboard1')  # Updated collection name

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
    leaderboard_ref = client.collection('leaderboard1')  # Updated collection name

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


# Function to update the leaderboard with the highest score
def update_leaderboard(student_id, class_number, username, high_score=None):
    leaderboard_ref = client.collection('leaderboard1')

    # Query for the specific student's record
    query = leaderboard_ref.where('student_id', '==', student_id).where('class', '==', class_number)
    records = query.stream()
    existing_record = [doc for doc in records]

    # If the record exists
    if existing_record:
        existing_high_score = existing_record[0].to_dict()['high_score']
        if high_score is not None and high_score > existing_high_score:
            existing_record[0].reference.update({'high_score': high_score, 'username': username})
        else:
            existing_record[0].reference.update({'username': username})
    else:
        # If the record does not exist, create a new one with high_score of 0 if high_score is None
        initial_high_score = high_score if high_score is not None else 0
        leaderboard_data = {
            'student_id': student_id,
            'class': class_number,
            'username': username,
            'high_score': initial_high_score
        }
        leaderboard_ref.add(leaderboard_data)

    print("Leaderboard updated.")


def hunt(player_status, hours_spent):
    aging_cost = hours_spent * (random.randint(1, player_status['age'] // 5 + 1) + random.uniform(0, 1))
    food_gained = 10 * math.sqrt(hours_spent) * random.uniform(0.8, 1.2)
    health_lost = aging_cost
    net_health_change = -health_lost
    net_food_change = food_gained
    return net_health_change, net_food_change


def rest(player_status, hours_spent):
    aging_cost = hours_spent * (random.randint(1, player_status['age'] // 5 + 1) + random.uniform(0, 1))
    health_gained = 8 * math.sqrt(hours_spent) * random.uniform(0.8, 1.2)
    food_lost = hours_spent * random.randint(1, 4)
    net_health_change = health_gained
    net_food_change = -food_lost
    return net_health_change, net_food_change


def get_player_status():
    return session['player_status']


def update_player_status(health_change, food_change, hunting_hours, resting_hours):
    player_status = session['player_status']
    player_status['prev_health'] = player_status['health']
    player_status['prev_food'] = player_status['food']
    player_status['health'] += health_change
    player_status['food'] += food_change
    player_status['health'] = max(0, min(player_status['health'], 100))
    player_status['food'] = max(0, min(player_status['food'], 100))
    player_status['log'].append({
        "age": player_status['age'],
        "health": player_status['health'],
        "food": player_status['food'],
        "net_health_change": player_status['health'] - player_status['prev_health'],
        "net_food_change": player_status['food'] - player_status['prev_food'],
        "hunting_hours": hunting_hours,
        "resting_hours": resting_hours
    })
    player_status['age'] += 1
    session['player_status'] = player_status


def reset_game_state():
    session['player_status'] = {
        "age": 18,
        "health": 50,
        "food": 50,
        "prev_health": 50,
        "prev_food": 50,
        "log": [{"age": 18, "health": 50, "food": 50,
                 "net_health_change": 0, "net_food_change": 0,
                 "hunting_hours": 0, "resting_hours": 0}]
    }
    return get_player_status()

def add_student_score(student_id, class_number, username, high_score):
    update_leaderboard(student_id, class_number, username, high_score)

def get_student_record(student_id, class_number):
    return students_df[(students_df['student_id'] == student_id) & (students_df['class'] == class_number)]

def calculate_high_score():
    player_status = session['player_status']
    return player_status['age']

@game1.route('/home1')
def home1():
    return render_template('home1.html')

@game1.before_request
def initialize_player_status():
    if 'player_status' not in session:
        session['player_status'] = {
            "age": 18,
            "health": 50,
            "food": 50,
            "prev_health": 50,
            "prev_food": 50,
            "has_played": False,  # Add this line
            "log": [{"age": 18, "health": 50, "food": 50,
                     "net_health_change": 0, "net_food_change": 0,
                     "hunting_hours": 0, "resting_hours": 0}]
        }


@game1.route("/get_game_state", methods=["GET"])
def get_game_state():
    return jsonify(get_player_status())

@game1.route("/reset_game", methods=["POST"])
def reset_game():
    player_status = reset_game_state()
    return jsonify(get_player_status())


@game1.route('/instructions1')
def instructions1():
    return render_template('instructions1.html')

@game1.route('/username_selection')
def main_username_selection():
    return render_template('main/username_selection.html')


@game1.route("/game1")
def play_game():
    player_status = get_player_status()
    if player_status['health'] <= 0 or player_status['food'] <= 0:
        high_score = calculate_high_score()
        student_id = session['student_id']
        class_number = session['class']
        username = session['username']
        update_leaderboard(student_id, class_number, username, high_score)
        reset_game_state()

    # Get the username from the session
    username = session.get('username', None)

    # Render the template and pass the player_status and username to the template
    return render_template("game1.html", player_status=get_player_status(), username=username)


@game1.route("/submit_decision", methods=["POST"])
def submit_decision():
    try:
        hunting_hours = int(request.form["hunting_hours"])
        resting_hours = int(request.form["resting_hours"])

        if hunting_hours + resting_hours == 24:
            net_health_change_hunt, net_food_change_hunt = hunt(get_player_status(), hunting_hours)
            net_health_change_rest, net_food_change_rest = rest(get_player_status(), resting_hours)

            net_health_change = net_health_change_hunt + net_health_change_rest
            net_food_change = net_food_change_hunt + net_food_change_rest

            update_player_status(net_health_change, net_food_change, hunting_hours, resting_hours)

            # Set the has_played flag to True
            player_status = get_player_status()
            player_status['has_played'] = True
            session['player_status'] = player_status

            result_message = f"You hunted for {hunting_hours} hours and rested for {resting_hours} hours. "
            result_message += f"Total health change for this period: {net_health_change:.2f}. "
            result_message += f"Total food change for this period: {net_food_change:.2f}."

            player_status = get_player_status()
            if player_status['health'] <= 0 or player_status['food'] <= 0:
                high_score = calculate_high_score()
                student_id = session['student_id']
                class_number = session['class']
                username = session['username']
                update_leaderboard(student_id, class_number, username, high_score)  # Call the update function
                result_message += " Game over!"

            status_dict = get_player_status()
            return jsonify({"result_message": result_message, "status": "success", "player_status": status_dict})
        else:
            return jsonify({"result_message": "Total hours must add up to 24. Please try again.", "status": "error"})

    except Exception as e:
        return jsonify({"result_message": str(e), "status": "error"})

@game1.route("/results")
def results():
    class_number = session.get('class', None) # Note that the key is 'class', not 'class_number'
    player_status = get_player_status()
    log_data = player_status['log']
    return render_template("results1.html", log=log_data, class_number=class_number)

@game1.route("/get_result_data", methods=["GET"])
def get_result_data():
    # Get player status and log data for the table and graph
    player_status = get_player_status()
    log_data = player_status['log']

    return jsonify({"age": player_status['age'],
                    "health": player_status['health'],
                    "food": player_status['food'],
                    "log": log_data})

@game1.route("/leaderboard/<int:class_number>")
def leaderboard1(class_number):
    leaderboard_df = read_leaderboard(class_number)
    leaderboard_df['high_score'] = to_numeric(leaderboard_df['high_score'], errors='coerce')
    scores = leaderboard_df.sort_values(by='high_score', ascending=False)
    return render_template("leaderboard1.html", scores=scores, class_number=class_number)
