from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from pynuts import Pynuts

CONFIG = {'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db',
          'PYNUTS_DOCUMENT_REPOSITORY': '/tmp/employees.git'}

app = Flask(__name__)
app.config.update(CONFIG)
app.db = SQLAlchemy(app)
nuts = Pynuts(app)
