from flask import Flask, render_template, session, redirect, request, flash, blueprints
from google.cloud import firestore

# Use the application's default credentials
client = firestore.Client()

main = blueprints.Blueprint('main', __name__, template_folder='templates')

@main.route('/')
def home():
    return render_template('index.html')

@main.route('/login', methods=['POST'])
def login():
    student_id = request.form['student_id']
    class_number = int(request.form['class'])

    # Reference to the Firestore collection where the students' data is stored
    students_ref = client.collection('students')

    # Query Firestore for the student ID and class number
    student_query = students_ref.where('student_id', '==', student_id).where('class', '==', class_number).get()

    # Check if the query returned any results
    student_exists = len(student_query) > 0

    if student_exists:
        # Set the student_id, class, and username in the session
        session['student_id'] = student_id
        session['class'] = class_number

        # Redirect to the username selection page
        return redirect("/username")
    else:
        flash('Invalid student ID or class number. Please try again.')
        return redirect('/')


@main.route('/username', methods=['GET', 'POST'])
def username_selection():
    student_id = session.get('student_id')

    # Query Firestore to get the existing username for this student ID
    user_ref = client.collection('students').document(student_id)
    user_doc = user_ref.get()
    existing_username = user_doc.get('username') if user_doc.exists else None

    if request.method == 'POST':
        username = request.form['username']

        # Update the username in Firestore
        user_ref.set({'username': username}, merge=True)

        session['username'] = username
        return redirect("/game")

    # Render the username selection page with the existing username (if any)
    return render_template('username_selection.html', existing_username=existing_username)

@main.route("/keep_username")
def keep_username():
    student_id = session.get('student_id')

    # Query Firestore to get the existing username for this student ID
    user_ref = client.collection('students').document(student_id)
    user_doc = user_ref.get()
    existing_username = user_doc.get('username') if user_doc.exists else None

    # Set the existing username in the session
    session['username'] = existing_username

    # Redirect to the game selection page
    return redirect("/game")


@main.route("/play_as_guest")
def play_as_guest():
    # Set up a temporary guest session
    session['username'] = "Guest"
    session['student_id'] = "guest"
    session['class'] = 0  # You can use 0 or any other identifier for guest class

    # Redirect to the game page or dashboard
    return redirect("/game")

@main.route("/logout")
def logout():
    session.clear()  # Clear the session
    return redirect("/")  # Redirect to the home page


@main.route("/game")
def game_selection():
    is_guest = session.get('student_id') == "guest"
    username = session.get('username', 'Guest')
    class_number = session.get('class', 0)
    return render_template("game_selection.html", username=username, is_guest=is_guest, class_number=class_number)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
