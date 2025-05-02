from flask import Flask
from flask_session import Session
from flask_wtf import CSRFProtect

app = Flask(__name__)  # create the instance of the flask class
app.secret_key = 'keyyyy'
csrf = CSRFProtect(app)

app.config['WTF_CSRF_ENABLED'] = False # I temporarily turned it off cause it breakes everything (Sofiya)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)