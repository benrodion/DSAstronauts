# -*- coding: utf-8 -*-

from flask import Flask, render_template, request

app = Flask(__name__)  # create the instance of the flask class

@app.route('/')
def login_or_sign_up():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True)