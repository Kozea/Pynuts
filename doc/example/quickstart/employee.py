from flask.ext.wtf import Form, TextField, IntegerField, Required

import pynuts

#The application
CONFIG = {
    'CSRF_ENABLED': False,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'}

app = pynuts.Pynuts(__name__, config=CONFIG)


#The database
class Employee(app.db.Model):
    __tablename__ = 'Employee'
    id = app.db.Column(app.db.Integer(), primary_key=True)
    name = app.db.Column(app.db.String())


#The view
class EmployeeView(app.ModelView):
    model = Employee
    list_column = 'name'

    class Form(Form):
        id = IntegerField(u'ID', validators=[Required()])
        name = TextField(u'Surname', validators=[Required()])


#The executable
@app.route('/')
def employees():
    return EmployeeView.list('list_employees.html')


@app.route('/add', methods=('POST', 'GET'))
def add_employee():
    return EmployeeView().create('add_employee.html',
                                      redirect='employees')

if __name__ == '__main__':
    app.db.create_all()  # Reflect app models in DB
    app.secret_key = 'Azerty'
    app.run(debug=True, host='127.0.0.1', port=5000)
