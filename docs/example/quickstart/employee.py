from flask import Flask
from wtforms import TextField, IntegerField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy

from pynuts import Pynuts
from pynuts.view import BaseForm


# The application
CONFIG = {
    'WTF_CSRF_ENABLED': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'}

app = Flask(__name__)
app.config.update(CONFIG)
app.db = SQLAlchemy(app)
nuts = Pynuts(app)


# The database
class Employee(app.db.Model):
    __tablename__ = 'Employee'
    id = app.db.Column(app.db.Integer(), primary_key=True)
    name = app.db.Column(app.db.String())


# The view
class EmployeeView(nuts.ModelView):
    model = Employee
    list_column = 'name'

    class Form(BaseForm):
        id = IntegerField('ID', validators=[Required()])
        name = TextField('Surname', validators=[Required()])


# The executable
@app.route('/')
def employees():
    return EmployeeView.list('list_employees.html')


@app.route('/add', methods=('POST', 'GET'))
def add_employee():
    return EmployeeView().create(
        'add_employee.html', redirect='employees')

if __name__ == '__main__':
    app.db.create_all()  # Reflect app models in DB
    app.secret_key = 'Azerty'
    app.run(debug=True, host='127.0.0.1', port=5000)
