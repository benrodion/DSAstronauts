# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session
from flask_session import Session

app = Flask(__name__)  # create the instance of the flask class

app.config["SESSION_PERMANENT"] = False # not sure if this is the right configuration
app.config["SESSION_TYPE"] = "filesystem" # not sure if this is the right configuration
Session(app)

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