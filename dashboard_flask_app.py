# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session
from flask_session import Session

app = Flask(__name__)  # create the instance of the flask class
app.config["SESSION_PERMANENT"] = False # not sure if this is the right configuration
app.config["SESSION_TYPE"] = "filesystem" # not sure if this is the right configuration
Session(app)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    selected_type = str(request.form.get("tripSelection"))
    trip_name = str(request.form.get("yourtripname"))
    if request.method == 'POST':
        if selected_type not in ['beach', 'dinner', 'skiing', 'museum', 'film', 'other']:
            return render_template('login_result.html', message ="Trip selection missing")
        elif trip_name == "":
            return render_template('login_result.html', message ="Trip name missing")

        session["trip_type"] = selected_type
        session["trip_name"] = trip_name
        
        return redirect('/transactions')
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(debug=True)

def button_trip_type(selection:str) -> str:
    if selection == str(selection):
        return "Great you have selected a trip!"



 # --- PLACEHOLDER FOR FUTURE INPUT LOGIC ---
# These are examples of ideas to explore later.

# TODO: Allow user to either select a trip OR write one manually
# if trip_inputed == "" and trip_button == "":
#     return render_template('dashboard.html',
#                            printed_result='Either select a trip or input one to continue.')

# try:
#     trip_button, trip  # figure out how to save in flask sessions
# except ValueError:
#     return render_template('dashboard.html', printed_result="Cannot create trip with this input.")

