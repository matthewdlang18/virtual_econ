from flask import Flask, Blueprint, session, render_template, request, redirect, url_for, jsonify
from google.cloud import firestore
from random import gauss, uniform
from numpy.random import multivariate_normal
import numpy as np
import logging
logging.basicConfig(level=logging.INFO)


macro3 = Blueprint('macro3', __name__, template_folder='templates')

client = firestore.Client()

# Asset parameters
asset_params = {
    "S&P500": {"avg_return": 0.1151, "std_dev": 0.1949, "min": -0.43, "max": 0.50},
    "Bonds": {"avg_return": 0.0334, "std_dev": 0.0301, "min": 0.0003, "max": 0.14},
    "Real Estate": {"avg_return": 0.0439, "std_dev": 0.0620, "min": -0.12, "max": 0.24},
    "Gold": {"avg_return": 0.0648, "std_dev": 0.2076, "min": -0.32, "max": 1.25},
    "Commodities": {"avg_return": 0.0815, "std_dev": 0.1522, "min": -0.25, "max": 2.00},
    "Bitcoin": {"avg_return": 0.50, "std_dev": 1.00, "min": -0.73, "max": 4.50}
}

# Define the correlation matrix for your assets
correlation_matrix = np.array([
    [1.0000, -0.5169, 0.3425, 0.0199, 0.1243, 0.4057],
    [-0.5169, 1.0000, 0.0176, 0.0289, -0.0235, -0.2259],
    [0.3425, 0.0176, 1.0000, -0.4967, -0.0334, 0.1559],
    [0.0199, 0.0289, -0.4967, 1.0000, 0.0995, -0.5343],
    [0.1243, -0.0235, -0.0334, 0.0995, 1.0000, 0.0436],
    [0.4057, -0.2259, 0.1559, -0.5343, 0.0436, 1.0000]
])

@macro3.route('/home', methods=['GET'])
def home():
    return render_template('macro3_home.html')

@macro3.route('/initialize_game', methods=['POST'])
def initialize_game():
    student_id = session['student_id']

    if student_id != 'professor':  # Only 'professor' is allowed to initialize the game
        return jsonify({"status": "Unauthorized"}), 401

    class_number = session.get('class', None)  # Fetch the class from the session

    # Initialize Firestore document for the game state
    game_ref = client.collection('macro3_game_states').document(str(class_number))
    game_ref.set({
        "class": class_number,
        "round_number": 0,
        "CPI": 100,
        "asset_prices": {
            "S&P500": 100,
            "Bonds": 100,
            "Real Estate": 10000,
            "Gold": 2000,
            "Commodities": 100,
            "Bitcoin": 25000,
        },
        "asset_price_history": {},
        "CPI_history": {},
        "asset_return_history": {},
        "bitcoin_shock_range": [-0.5, -0.75],
        'extreme_bitcoin_event': False,
        'total_cash_injected': 0,
    })

    # Initialize each student's portfolio
    students_ref = client.collection(f'macro3_students_class_{class_number}')
    students = students_ref.stream()

    for student in students:
        student_ref = students_ref.document(student.id)
        student_ref.set({
            "cash": 5000,
            "portfolio": {
                "assets": {}
            },
            "trade_history": []
        })

    return jsonify({"status": "Game and student portfolios initialized"})

@macro3.route('/next_round', methods=['POST'])
def next_round():
    class_number = session.get('class', None)
    if class_number is None:
        return "Class number not found in session", 400
    # Advance to the next round and update asset prices
    game_ref = client.collection('macro3_game_states').document(str(class_number))
    game_state = game_ref.get().to_dict()
    participating_class = game_state.get('class', None)

    if participating_class is None:
        return jsonify({"status": "No class participating"})

    # Initialize or update the round number of the last Bitcoin crash
    last_bitcoin_crash_round = game_state.get('last_bitcoin_crash_round', 0)
    current_bitcoin_shock_range = game_state.get('bitcoin_shock_range', [-0.5, -0.75])

    # Fetch extreme_bitcoin_event status
    extreme_bitcoin_event = game_state.get('extreme_bitcoin_event', False)

    # Update round number
    game_state['round_number'] += 1

    previous_asset_returns = game_state.get('asset_return_history', {}).get(str(game_state['round_number'] - 1), {})

    # Update Bitcoin's parameters based on its current price
    bitcoin_price = game_state['asset_prices']['Bitcoin']
    new_avg_return, new_std_dev = adjust_bitcoin_params(bitcoin_price, extreme_bitcoin_event)
    asset_params['Bitcoin']['avg_return'] = new_avg_return
    asset_params['Bitcoin']['std_dev'] = new_std_dev

    if bitcoin_price >= 1000000 and not extreme_bitcoin_event:
        game_state['extreme_bitcoin_event'] = True

    std_devs = np.array([params['std_dev'] for asset, params in asset_params.items()])
    covariance_matrix = np.outer(std_devs, std_devs) * correlation_matrix

    mean_returns = [params['avg_return'] for asset, params in asset_params.items()]
    correlated_returns = multivariate_normal(mean_returns, covariance_matrix)

    new_asset_prices = {}
    new_asset_returns = {}
    for i, (asset, params) in enumerate(asset_params.items()):
        if asset == "Bitcoin":
            if bitcoin_price < 10000:
                raw_return = uniform(2, 4)  # Return between 200% and 400%
            elif bitcoin_price >= 1000000 and not extreme_bitcoin_event:
                raw_return = uniform(-0.3, -0.2)  # Return between -30% and -20%
            else:
                previous_return = previous_asset_returns.get(asset, 0)
                raw_return = 0.7 * correlated_returns[i] + 0.3 * previous_return

            # Existing logic for Bitcoin crashes...
            if game_state['round_number'] - last_bitcoin_crash_round >= 4:
                if np.random.rand() < 0.5:
                    raw_return = np.random.uniform(current_bitcoin_shock_range[0], current_bitcoin_shock_range[1])
                    last_bitcoin_crash_round = game_state['round_number']
                    new_shock_range = [
                        max(current_bitcoin_shock_range[0] + 0.1, -0.05),
                        max(current_bitcoin_shock_range[1] + 0.1, -0.15)
                    ]
                    game_state['bitcoin_shock_range'] = new_shock_range
        else:
            previous_return = previous_asset_returns.get(asset, 0)
            raw_return = 0.7 * correlated_returns[i] + 0.3 * previous_return

        if previous_return > 0.2:
            if np.random.rand() < 0.3:
                raw_return = -abs(raw_return)

        if np.random.rand() < 0.05:
            shock = np.random.uniform(-0.2, 0.2)
            raw_return += shock

        new_return = max(min(raw_return, params['max']), params['min'])
        if asset == "Bitcoin" and new_return == params['min']:
            new_return = uniform(-0.8, -0.7)
        new_price = game_state['asset_prices'][asset] * (1 + new_return)
        new_asset_prices[asset] = new_price
        new_asset_returns[asset] = new_return

    game_state['asset_price_history'][str(game_state['round_number'])] = new_asset_prices
    game_state['asset_return_history'][str(game_state['round_number'])] = new_asset_returns
    game_state['last_bitcoin_crash_round'] = last_bitcoin_crash_round

    avg_cpi_increase = 0.025
    std_dev_cpi_increase = 0.015

    new_cpi_increase = gauss(avg_cpi_increase, std_dev_cpi_increase)
    new_cpi = game_state['CPI'] * (1 + new_cpi_increase)
    game_state['CPI_history'][str(game_state['round_number'])] = new_cpi

    game_state['asset_prices'] = new_asset_prices
    game_state['CPI'] = new_cpi

    students_ref = client.collection(f'macro3_students_class_{participating_class}')
    students = students_ref.stream()

    for student in students:
        student_data = student.to_dict()
        portfolio = student_data['portfolio']

        for asset_name, quantity in portfolio.items():
            if asset_name in new_asset_prices:
                new_price = new_asset_prices[asset_name]
                max_affordable_quantity = int(student_data['cash'] // new_price)
                new_quantity = min(quantity, max_affordable_quantity)

                portfolio[asset_name] = new_quantity
                student_data['cash'] -= (new_quantity - quantity) * new_price

        avg_cash_injection = 5000 * np.sqrt(game_state['round_number'])
        std_dev_injection = avg_cash_injection * 0.25
        random_injection = gauss(avg_cash_injection, std_dev_injection)
        student_data['cash'] += random_injection
        student_data['latest_cash_injection'] = random_injection

        if 'total_cash_injected' not in student_data:
            student_data['total_cash_injected'] = 0

        student_data['total_cash_injected'] += random_injection

        # Ensure the cash_injection_history list exists in student_data
        if 'cash_injection_history' not in student_data:
            student_data['cash_injection_history'] = []

        # Ensure the cash_injection_history list is long enough to hold data for the current round
        while len(student_data['cash_injection_history']) <= game_state['round_number']:
            student_data['cash_injection_history'].append(0.0)

        # Update the cash injection for the current round
        student_data['cash_injection_history'][game_state['round_number']] = random_injection
        print(
            f"Student {student.id} injected {random_injection} in round {game_state['round_number']}")  # Debugging line

        # Print the student's portfolio
        print(f"Student {student.id}'s portfolio: {portfolio}")  # <-- Added this line

        total_portfolio_value = student_data['cash']

        for asset_name, quantity in portfolio.items():
            if asset_name in new_asset_prices:
                asset_value = new_asset_prices[asset_name] * quantity
                total_portfolio_value += asset_value
                print(f"Student {student.id} has {quantity} of {asset_name} worth {asset_value}")

        # Now, calculate the total portfolio value, considering both the cash and the assets
        total_portfolio_value = student_data['cash']
        for asset_name, quantity in portfolio.get('assets', {}).items():
            if asset_name in new_asset_prices:
                asset_value = new_asset_prices[asset_name] * quantity
                total_portfolio_value += asset_value

        # Update the portfolio_value_history
        if 'portfolio_value_history' not in student_data:
            student_data['portfolio_value_history'] = []
        student_data['portfolio_value_history'].append(total_portfolio_value)

        # Ensure the portfolio_value_history list is long enough to hold data for the current round
        while len(student_data['portfolio_value_history']) <= game_state['round_number']:
            student_data['portfolio_value_history'].append(0.0)

        # Update the portfolio value for the current round
        student_data['portfolio_value_history'][game_state['round_number']] = total_portfolio_value

        # Store the asset prices for the current round for this student
        if 'asset_prices_history' not in student_data:
            student_data['asset_prices_history'] = {}
        student_data['asset_prices_history'][str(game_state['round_number'])] = new_asset_prices

        students_ref.document(student.id).set(student_data)

    game_ref.set(game_state)

    return jsonify({"status": "Advanced to next round", "new_state": game_state})


# Function to adjust Bitcoin's parameters based on its price
def adjust_bitcoin_params(bitcoin_price, extreme_bitcoin_event):
    base_avg_return = 0.50
    base_std_dev = 1.00

    if bitcoin_price < 10000:
        return uniform(2, 4), 0  # Return between 200% and 400% with 0 standard deviation

    if bitcoin_price >= 1000000:
        if not extreme_bitcoin_event:  # If this is the first time Bitcoin has reached 1 million
            return uniform(-0.3, -0.2), 0  # Return between -30% and -20% with 0 standard deviation

    price_threshold = 100000

    # Calculate the number of 100k increments above the threshold
    increments_above_threshold = max(0, (bitcoin_price - price_threshold) // 50000)

    # Adjust average return and standard deviation
    avg_return = max(0.05, base_avg_return - increments_above_threshold * 0.1)
    std_dev = max(0.01, base_std_dev - increments_above_threshold * 0.20)

    return avg_return, std_dev

@macro3.route('/professor_dashboard', methods=['GET'])
def professor_dashboard():
    student_id = session.get('student_id', None)
    class_number = session.get('class', None)
    if class_number is None:
        return "Class number not found in session", 400

    # Check if the logged-in user is the professor
    is_professor = (student_id == 'professor')

    if not is_professor:
        return jsonify({"status": "Unauthorized", "message": "You are not authorized to access this page."}), 403

    # Rest of your code for professor access
    # Fetch the current game state from Firestore
    game_ref = client.collection('macro3_game_states').document(str(class_number))
    game_state = game_ref.get().to_dict()

    if game_state:
        return jsonify({"status": "Game initialized", "data": game_state, "is_professor": is_professor})
    else:
        return jsonify({"status": "Game not initialized", "is_professor": is_professor})

@macro3.route('/professor_dashboard_page', methods=['GET'])
def professor_dashboard_page():
    student_id = session.get('student_id', None)

    # Check if the logged-in user is the professor
    is_professor = (student_id == 'professor')

    if not is_professor:
        return "Unauthorized. You are not authorized to access this page.", 403

    # Rest of your code for professor access
    # Assuming 'professor_dashboard.html' is the name of your HTML file
    return render_template('macro3_professor_dashboard.html')

@macro3.route('/check_professor', methods=['GET'])
def check_professor():
    student_id = session.get('student_id', None)
    is_professor = (student_id == 'professor')
    return jsonify({"is_professor": is_professor})


@macro3.route('/asset_dashboard', methods=['GET'])
def asset_dashboard():
    student_id = session['student_id']
    class_number = session.get('class', None)
    if class_number is None:
        return "Class number not found in session", 400

    # Fetch the current game state from Firestore
    game_ref = client.collection('macro3_game_states').document(str(class_number))
    game_state = game_ref.get().to_dict()

    if game_state:
        return jsonify({"status": "Game initialized", "data": game_state})
    else:
        return jsonify({"status": "Game not initialized"})

@macro3.route('/asset_dashboard_page', methods=['GET'])
def asset_dashboard_page():
    return render_template('macro3_asset_dashboard.html')


@macro3.route('/student_dashboard', methods=['GET'])
def student_dashboard_page():
    # Fetch the student's portfolio from Firestore to see if it exists
    student_id = session.get('student_id', "Unknown")
    class_number = session.get('class', "Unknown")  # Assuming class number is stored in the session

    print(f"Checking data for Student ID: {student_id}, Class: {class_number}")  # Debugging line

    student_ref = client.collection(f'macro3_students_class_{class_number}').document(student_id)
    student = student_ref.get()

    if not student.exists:
        print(f"No data found for Student ID: {student_id}, Class: {class_number}. Initializing...")  # Debugging line
        try:
            student_ref.set({
                "cash": 5000,
                "portfolio": {"assets": {}},
                "trade_history": []
            })
            print(f"Successfully initialized data for Student ID: {student_id}, Class: {class_number}")  # Debugging line
        except Exception as e:
            print(f"Failed to initialize data for Student ID: {student_id}, Class: {class_number}")  # Debugging line
            print("Error:", e)

    # Assuming 'macro3_student_dashboard.html' is the name of your HTML file for the student dashboard
    return render_template('macro3_student_dashboard.html')

@macro3.route('/student_dashboard_data', methods=['GET'])
def student_dashboard_data():
    class_number = session.get('class', None)
    if class_number is None:
        return "Class number not found in session", 400

    # Fetch the game state from Firestore
    game_ref = client.collection('macro3_game_states').document(str(class_number))
    game_state = game_ref.get().to_dict()

    # Fetch the student's portfolio from Firestore
    student_id = session.get('student_id', "Unknown")
    class_number = session.get('class', "Unknown")

    student_ref = client.collection(f'macro3_students_class_{class_number}').document(student_id)
    student = student_ref.get()

    if student.exists:
        student_data = student.to_dict()
        # Print the entire student_data for debugging
        logging.info(f"Complete data for Student {student_id}: {student_data}")  # <-- Add this

        # Get current asset prices
        current_asset_prices = game_state.get('asset_prices', {})

        # Get student's portfolio
        portfolio = student_data.get('portfolio', {}).get('assets', {})

        # Calculate current portfolio value
        current_portfolio_value = sum([portfolio[asset] * current_asset_prices.get(asset, 0) for asset in portfolio])

        # Add cash to the total portfolio value
        cash = student_data.get('cash', 0)
        current_portfolio_value += cash

        # Update the leaderboard with the latest portfolio value and total cash injected
        total_cash_injected = sum(student_data.get('cash_injection_history', []))
        username = session.get('username')
        update_leaderboard_macro3(student_id, username, class_number, current_portfolio_value, total_cash_injected)

        # Print the current portfolio value
        print(f"Student {student_id}'s current portfolio value: {current_portfolio_value}")

        # Print the portfolio value history
        portfolio_value_history = student_data.get('portfolio_value_history', [])
        logging.info(f"Length of portfolio_value_history for Student {student_id}: {len(portfolio_value_history)}")  # <-- Add this
        for i, value in enumerate(portfolio_value_history):
            print(f"Round {i}: {value}")

        # Build the response data
        response_data = {
            "status": "Fetched portfolio and game state",
            "data": {
                "game_state": game_state,
                "portfolio": student_data.get('portfolio', {}),
                "cash": cash,
                "latest_cash_injection": student_data.get('latest_cash_injection', 0),
                "cash_injection_history": student_data.get('cash_injection_history', []),
                "trade_history": student_data.get('trade_history', []),
                "portfolio_value": current_portfolio_value,
                "portfolio_value_history": student_data.get('portfolio_value_history', [])
            }
        }
        return jsonify(response_data)
    else:
        return jsonify({"status": "Could not fetch data"})


@macro3.route('/instructions', methods=['GET'])
def instructions():
    asset_params = {
        "S&P500": {"avg_return": 0.1151, "std_dev": 0.1949, "min": -0.43, "max": 0.50},
        "Bonds": {"avg_return": 0.0334, "std_dev": 0.0301, "min": 0.0003, "max": 0.14},
        "Real Estate": {"avg_return": 0.0439, "std_dev": 0.0620, "min": -0.12, "max": 0.24},
        "Gold": {"avg_return": 0.0648, "std_dev": 0.2076, "min": -0.32, "max": 1.25},
        "Commodities": {"avg_return": 0.0815, "std_dev": 0.1522, "min": -0.25, "max": 2.00},
        "Bitcoin": {"avg_return": 0.50, "std_dev": 1.00, "min": -0.73, "max": 4.50}
    }
    return render_template('macro3_instructions.html', asset_params=asset_params)

@macro3.route('/student_portfolio_page', methods=['GET'])
def student_portfolio_page():
    return render_template('macro3_student_portfolio_page.html')


@macro3.route('/buy_asset', methods=['POST'])
def buy_asset():
    student_id = session['student_id']
    asset_name = request.json['asset_name']
    quantity = float(request.json['quantity'])
    class_number = session['class']

    print(f"Attempting to buy {quantity} of {asset_name} for {student_id}")  # Debugging line

    # Fetch current game state to get asset prices
    game_ref = client.collection('macro3_game_states').document(str(class_number))
    game_data = game_ref.get().to_dict()
    asset_price = game_data['asset_prices'][asset_name]

    # Fetch student data to update portfolio and cash
    student_ref = client.collection(f'macro3_students_class_{class_number}').document(student_id)
    student_data = student_ref.get().to_dict()

    total_cost = asset_price * quantity
    if student_data['cash'] < total_cost:
        return jsonify({"status": "Insufficient funds"})

    # Update portfolio and cash
    student_data['cash'] -= total_cost
    student_data['portfolio']['assets'][asset_name] = student_data['portfolio']['assets'].get(asset_name, 0) + quantity  # UPDATED LINE
    student_data['trade_history'].append({
        "action": "buy",
        "asset": asset_name,
        "quantity": quantity,
        "price": asset_price,
        'round': game_data['round_number']
    })

    student_ref.set(student_data)
    return jsonify({"status": "Asset bought"})


@macro3.route('/sell_asset', methods=['POST'])
def sell_asset():
    student_id = session['student_id']
    asset_name = request.json['asset_name']
    quantity = float(request.json['quantity'])
    class_number = session['class']

    # Fetch current game state to get asset prices
    game_ref = client.collection('macro3_game_states').document(str(class_number))
    game_data = game_ref.get().to_dict()
    asset_price = game_data['asset_prices'][asset_name]

    # Fetch student data to update portfolio and cash
    student_ref = client.collection(f'macro3_students_class_{class_number}').document(student_id)
    student_data = student_ref.get().to_dict()

    if student_data['portfolio']['assets'].get(asset_name, 0) < quantity:
        return jsonify({"status": "Insufficient assets"})

    student_data['cash'] += asset_price * quantity
    student_data['portfolio']['assets'][asset_name] -= quantity  # UPDATED LINE
    student_data['trade_history'].append({
        "action": "sell",
        "asset": asset_name,
        "quantity": quantity,
        "price": asset_price,
        'round': game_data['round_number']
    })

    if student_data['portfolio']['assets'][asset_name] == 0:
        del student_data['portfolio']['assets'][asset_name]


    student_ref.set(student_data)
    return jsonify({"status": "Asset sold"})


@macro3.route('/student_portfolio_history', methods=['GET'])
def student_portfolio_history():
    # Fetch the student's portfolio from Firestore
    student_id = session.get('student_id', "Unknown")
    class_number = session.get('class', "Unknown")

    student_ref = client.collection(f'macro3_students_class_{class_number}').document(student_id)
    student = student_ref.get()

    if student.exists:
        student_data = student.to_dict()
        portfolio_value_history = student_data.get('portfolio_value_history', [])

        # Print the portfolio history for debugging
        print(f"Student {student_id}'s portfolio value history: {portfolio_value_history}")
    else:
        return jsonify({"status": "Could not fetch data"})

    return jsonify({
        "data": {
            "rounds": list(range(len(portfolio_value_history))),
            "values": portfolio_value_history
        }
    })


def update_leaderboard_macro3(student_id, username, class_number, portfolio_value, total_cash_injected):
    doc_ref = client.collection('macro3_leaderboard').document(student_id)
    doc_ref.set({
        'student_id': student_id,
        'username': username,
        'class_number': class_number,
        'portfolio_value': portfolio_value,
        'total_cash_injected': total_cash_injected
    }, merge=True)

def get_leaderboards_macro3(class_number):
    all_scores = client.collection('macro3_leaderboard').stream()
    all_data = [{'id': doc.id, **doc.to_dict()} for doc in all_scores]
    filtered_data = [entry for entry in all_data if entry.get('class_number') == class_number]

    # Calculate ROI for each student
    for entry in filtered_data:
        total_injected = entry.get('total_cash_injected', 0) + 5000
        portfolio_value = entry.get('portfolio_value', 0)

        # Print the total cash injected
        print(f"Student {entry['student_id']} total cash injected: {total_injected}")
        print(f"Student {entry['student_id']} portfolio value: {portfolio_value}")

        entry['ROI'] = (portfolio_value - total_injected) / total_injected

        # Print the ROI
        print(f"Student {entry['student_id']} ROI: {entry['ROI']}")

    portfolio_leaderboard = sorted(filtered_data, key=lambda x: x['portfolio_value'], reverse=True)[:25]
    roi_leaderboard = sorted(filtered_data, key=lambda x: x['ROI'], reverse=True)[:25]

    return portfolio_leaderboard, roi_leaderboard



@macro3.route('/leaderboard', methods=['GET'])
def macro3_leaderboard():
    class_number = session.get('class')
    if not class_number:
        return render_template('macro3_leaderboard.html', portfolio_leaderboard=[], roi_leaderboard=[])

    portfolio_leaderboard, roi_leaderboard = get_leaderboards_macro3(class_number)
    print(portfolio_leaderboard)  # Debugging statement
    print(roi_leaderboard)  # Debugging statement
    return render_template('macro3_leaderboard.html', portfolio_leaderboard=portfolio_leaderboard, roi_leaderboard=roi_leaderboard)
