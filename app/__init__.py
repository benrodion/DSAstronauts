from flask import Flask

app = Flask(__name__)  # create the instance of the flask class

# Import routes so they register with the app
from app import routes