# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session
from flask_session import Session

app = Flask(__name__)  # create the instance of the flask class
app.config["SESSION_PERMANENT"] = False # not sure if this is the right configuration
app.config["SESSION_TYPE"] = "filesystem" # not sure if this is the right configuration
Session(app)


@app.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if not request.form.get("tripSelection"):
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


if __name__ == "__main__":
    app.run(debug=True)

def button_trip_type(selection:str) -> bool:
    if selection == str(selection):
        return "Great you have selected a trip!"



 if trip_inputed == "" and trip_button == "":
            return render_template('dashboard.html',
                                   printed_result='Either select a trip or inpute one to continue to transactions.')

try:
            trip_button, trip #figure out how to save in flask sessions
        except ValueError:
            return render_template('dashboard.html', printed_result="Cannot creat trip with this input.")

