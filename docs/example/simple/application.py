from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from pynuts import Pynuts

CONFIG = {
    'CSRF_ENABLED': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'}

app = Flask(__name__)
app.config.update(CONFIG)
app.db = SQLAlchemy(app)
nuts = Pynuts(app)
