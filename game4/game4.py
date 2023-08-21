from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from google.cloud import firestore
import random

game4 = Blueprint('game4', __name__, template_folder='templates')

client = firestore.Client()


@game4.route('/home4')
def home4():
    return render_template('home4.html')

@game4.route('/leaderboard/<int:class_number>')
def leaderboard(class_number):
    students = get_leaderboard(class_number)
    return render_template('game4_leaderboard.html', class_number=class_number, students=students)

@game4.route('/instructions')
def instructions():
    current_username = session.get('username')
    return render_template('game4_instructions.html', current_username=current_username)

