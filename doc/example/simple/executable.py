from flaskext.wtf import (Form, TextField, Required)
from sqlalchemy.ext.hybrid import hybrid_property

import pynuts

CONFIG = {'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'}

app = pynuts.Pynuts(__name__, config=CONFIG)


class Employee(app.db.Model):
        __tablename__ = 'Employee'
        id = app.db.Column(app.db.Integer(), primary_key=True)
        name = app.db.Column(app.db.String())
        firstname = app.db.Column(app.db.String())

        @hybrid_property
        def fullname(self):
            return '%s - %s' % (self.firstname, self.name)


class EmployeeView(app.ModelView):
    model = Employee

    list_column = 'fullname'
    create_columns = ('name', 'firstname')

    class Form(Form):
        name = TextField(u'Surname', validators=[Required()])
        firstname = TextField(u'Firstname', validators=[Required()])


@app.route('/')
@app.route('/employees/')
def employees():
    return EmployeeView.list('list_employees.html')


@app.route('/employee/add/', methods=('POST', 'GET'))
def add_employee():
    return EmployeeView().create('add_employee.html',
                                      redirect='employees')


if __name__ == '__main__':
    app.db.create_all()
    app.secret_key = 'Azerty'
    app.run(debug=True, host='127.0.0.1', port=5000)
