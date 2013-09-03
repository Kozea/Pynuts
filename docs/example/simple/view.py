from wtforms import TextField, IntegerField
from wtforms.validators import Required
from pynuts.view import BaseForm

import database
from application import nuts


class EmployeeView(nuts.ModelView):
    model = database.Employee

    list_column = 'fullname'
    create_columns = ('name', 'firstname')

    class Form(BaseForm):
        id = IntegerField(u'ID')
        name = TextField(u'Surname', validators=[Required()])
        firstname = TextField(u'Firstname', validators=[Required()])
        fullname = TextField(u'Fullname')
