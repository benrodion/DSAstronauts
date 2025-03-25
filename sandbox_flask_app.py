# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session
from flask_session import Session

app = Flask(__name__)  # create the instance of the flask class
app.config["SESSION_PERMANENT"] = False # not sure if this is the right configuration
app.config["SESSION_TYPE"] = "filesystem" # not sure if this is the right configuration
Session(app)

app = Flask(__name__)  # create the instance of the flask class

@app.route('/', methods=["GET","POST"])
def show_login_page():
    if request.method == "POST": # this implements login logic, but not signup yet
        if not request.form.get("loggroupid"):
            return render_template('login_result.html', message = "Group name missing")
        elif not request.form.get("logpass"):
            return render_template('login_result.html', message = "Password missing")
        session["groupid"] = request.form.get("loggroupid")
        session["password"] = request.form.get("logpass")
        return render_template('login_result.html', message = "You are logged in", name = request.form.get("loggroupid"))
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form.get("tripSelection") == "Choose...":
            return render_template('dashboard.html', message = "Trip selection missing")
        elif not request.form.get("yourtripname"):
            return render_template('dashboard.html', message = "Trip name missing")
        
        trip_buttion_str = str(request.form.get['tripSelection'])

        # make sure the input is one of the allowed inputs (not absolutely necessary in the drop-down case)
        if trip_buttion_str not in ['Beach Trip', 'Dinner', 'Skiing Trip', 'Museum Trip', 'Movies', 'Other']:
            return render_template('dashboard.html',
                                   printed_result='You must select one of the trip types.')
        
        session["trip_type"] = request.form.get['tripSelection']
        session["trip_name"] = request.form.get['yourtripname']
        return render_template('transactions.html', message = 'You have succefully created a trip!', trip_name = request.form.get("yourtripname"))

    return render_template('dashboard.html')