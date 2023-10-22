

@macro3.route('/student_dashboard_data', methods=['GET'])
def student_dashboard_data():
    # Fetch the game state from Firestore
    game_ref = client.collection('macro3_game_state').document('game_state')
    game_state = game_ref.get().to_dict()
    current_round = game_state.get('round_number', -1)  # Fetch current round

    # Fetch the student's portfolio from Firestore
    student_id = session.get('student_id', "Unknown")
    class_number = session.get('class', "Unknown")

    student_ref = client.collection(f'macro3_students_class_{class_number}').document(student_id)
    student = student_ref.get()

    if student.exists:
        student_data = student.to_dict()
        last_round = student_data.get('last_round', -1)

        # Existing logic to update the portfolio, cash, etc.
        cash = student_data['cash']
        assets = student_data['portfolio']['assets']
        asset_prices = game_state['asset_prices']

        # Calculate the total portfolio value
        portfolio_value = cash
        for asset, quantity in assets.items():
            portfolio_value += asset_prices.get(asset, 0) * quantity

        username = session.get('username', "Unknown")
        update_leaderboard_macro3(student_id, username, class_number, portfolio_value)

        trade_history = student_data.get('trade_history', [])

        portfolio_value_history = student_data.get('portfolio_value_history', [])
        cash_injection_history = student_data.get('cash_injection_history', [])
        print(f"Portfolio value history: {portfolio_value_history}")  # Debugging line
        print(f"Cash injection history: {cash_injection_history}")  # Debugging line

        # Filling missed rounds
        num_missing_rounds = current_round - len(portfolio_value_history)

        for i in range(num_missing_rounds):
            round_number = len(portfolio_value_history)
            cash_injection = student_data.get('cash_injection_history', [0] * current_round)[round_number]
            cash += cash_injection  # Update the student's cash with the cash injection for the missed round

            # Use asset prices for the specific round to compute the portfolio value
            asset_prices_for_round = student_data.get('asset_prices_history', {}).get(str(round_number),
                                                                                      game_state['asset_prices'])

            portfolio_value_for_missed_round = cash
            for asset, quantity in assets.items():
                portfolio_value_for_missed_round += asset_prices_for_round.get(asset, 0) * quantity

            portfolio_value_history.append(portfolio_value_for_missed_round)
            cash_injection_history.append(cash_injection)

        # Append the current round's portfolio value if this round is not a missed round
        if last_round != current_round:
            portfolio_value_history.append(portfolio_value)

        # Update Firestore with the computed values
        student_ref.update({
            'portfolio_value_history': portfolio_value_history,
            'cash_injection_history': cash_injection_history,
            'last_round': current_round
        })

        response_data = {
            "status": "Fetched portfolio and game state",
            "data": {
                "game_state": game_state,
                "portfolio": student_data['portfolio'],
                "cash": student_data['cash'],
                "latest_cash_injection": student_data.get('latest_cash_injection', 0),
                "cash_injection_history": cash_injection_history,
                "trade_history": trade_history,
                "portfolio_value": portfolio_value,
                "portfolio_value_history": portfolio_value_history
            }
        }
        return jsonify(response_data)
    else:
        return jsonify({"status": "Could not fetch data"})