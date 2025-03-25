# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session
from database import SessionLocal, UserGroup
from flask_session import Session

app = Flask(__name__)  # create the instance of the flask class

app.config["SESSION_PERMANENT"] = False # not sure if this is the right configuration
app.config["SESSION_TYPE"] = "filesystem" # not sure if this is the right configuration
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
        user = db.query(UserGroup).filter(UserGroup.username == groupid, UserGroup.password == password).first()
        db.close()

        if user:
            session["groupid"] = groupid
            return render_template('login_result.html', message="You are logged in", name=groupid)
        else:
            return render_template('login_result.html', message="Invalid username or password")

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

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    print("✅ Starting Flask app...")
    app.run(debug=True, use_reloader=False)
