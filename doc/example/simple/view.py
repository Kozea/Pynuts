from flaskext.wtf import (Form, TextField, Required)

import database
from application import app


class EmployeeView(app.ModelView):
    model = database.Employee

    list_column = 'fullname'
    create_columns = ('name', 'firstname')

    class Form(Form):
        name = TextField(u'Surname', validators=[Required()])
        firstname = TextField(u'Firstname', validators=[Required()])
