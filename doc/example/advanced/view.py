from flaskext.wtf import (Form, TextField, IntegerField, Required)

import database
from application import app


class EmployeeView(app.ModelView):
    model = database.Employee

    list_column = 'fullname'
    create_columns = ('name', 'firstname')
    view_columns = ('id', 'name', 'firstname', 'fullname')
    edit_columns = ('name', 'firstname')
    table_columns = ('fullname', )

    class Form(Form):
        id = IntegerField('ID')
        name = TextField(u'Surname', validators=[Required()])
        firstname = TextField(u'Firstname', validators=[Required()])
        fullname = TextField('Employee name')
