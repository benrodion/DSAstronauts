# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session
from database import SessionLocal, UserGroup, Transaction 
from flask_session import Session
import bcrypt
from helpers import check_bad_password

app = Flask(__name__)  # create the instance of the flask class

app.config["SESSION_PERMANENT"] = False  # not sure if this is the right configuration
app.config["SESSION_TYPE"] = "filesystem"  # not sure if this is the right configuration
Session(app)

@app.route('/', methods=["GET", "POST"])
def show_login_page():
    if request.method == "POST":
        groupid = request.form.get("loggroupid")
        password = request.form.get("logpass")

        if not groupid:
            return render_template('login_result.html', message="Group name missing")
        elif not password:
            return render_template('login_result.html', message="Password missing")

        # Create a database session
        db = SessionLocal()
        user = db.query(UserGroup).filter(UserGroup.username == groupid).first()
        db.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            session["groupid"] = groupid
            return redirect('/dashboard')
        else:
            return render_template('login_result.html', message="Invalid username or password")

    return render_template('login.html')
    return render_template('login.html')

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("newloggroupid")
        password = request.form.get("newlogpass")

        print("Received Sign-Up Data:")  # Debugging
        print("Username:", username)
        print("Password:", password)

        if not username or not password:
            return render_template('signup_result.html', message="Username or password missing")
        
        if check_bad_password(password):
            return render_template('signup_result.html', message=check_bad_password(password))

        db = SessionLocal()

        # Check if username exists
        existing_user = db.query(UserGroup).filter(UserGroup.username == username).first()
        if existing_user:
            db.close()
            return render_template('signup_result.html', message="Username already exists")

        # Hash password (for security)
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = UserGroup(username=username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.close()

        return render_template('signup_result.html', message="Sign-up successful!")

    return render_template('signup.html')



@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form.get("tripSelection") == "Choose...":
            return render_template('dashboard.html', message="Trip selection missing")
        elif not request.form.get("yourtripname"):
            return render_template('dashboard.html', message="Trip name missing")

        trip_button_str = str(request.form.get('tripSelection'))

        # make sure the input is one of the allowed inputs (not absolutely necessary in the drop-down case)
        if trip_button_str not in ['Beach Trip', 'Dinner', 'Skiing Trip', 'Museum Trip', 'Movies', 'Other']:
            return render_template('dashboard.html',
                                   printed_result='You must select one of the trip types.')

        session["trip_type"] = request.form.get('tripSelection')
        session["trip_name"] = request.form.get('yourtripname')
        return render_template('transactions.html', message='You have successfully created a trip!', trip_name=request.form.get("yourtripname"))

    return render_template('dashboard.html')

if __name__ == "__main__":
    print("✅ Starting Flask app...")
    app.run(debug=True, use_reloader=False)