from flask.ext.wtf import (Form, TextField, IntegerField,
                          PasswordField, Required)

import database
from application import app


class EmployeeView(app.ModelView):
    model = database.Employee

    list_column = 'fullname'
    table_columns = ('fullname', )
    create_columns = ('login', 'password', 'name', 'firstname')
    read_columns = ('person_id', 'name', 'firstname', 'fullname')
    update_columns = ('name', 'firstname')

    class Form(Form):
        person_id = IntegerField('ID')
        login = TextField(u'Login', validators=[Required()])
        password = PasswordField(u'Password', validators=[Required()])
        name = TextField(u'Surname', validators=[Required()])
        firstname = TextField(u'Firstname', validators=[Required()])
        fullname = TextField('Employee name')
