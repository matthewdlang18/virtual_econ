from flask import Blueprint, session, render_template, jsonify, request
from google.cloud import firestore
import hashlib
import time

mining = Blueprint('mining', __name__, template_folder='templates')

# Initialize Firestore client
client = firestore.Client()

def calculate_hash(data):
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

@mining.route('/home', methods=['GET'])
def home():
    return render_template('mining_home.html')

@mining.route('/instructions', methods=['GET'])
def instructions():
    return render_template('mining_instructions.html')

@mining.route('/game', methods=['GET', 'POST'])
def game():
    hash_result = None
    if request.method == 'POST':
        previous_hash = request.form['previous_hash']
        transaction = request.form['transaction']
        block_reward = request.form['block_reward']
        nonce = request.form['nonce']

        # Concatenate the input data
        input_data = f"{previous_hash}{transaction}{block_reward}{nonce}"
        # Calculate the SHA-256 hash
        hash_result = calculate_hash(input_data)

    return render_template('mining_game.html', hash_result=hash_result)
