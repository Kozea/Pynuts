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
        id = IntegerField('ID')
        name = TextField('Surname', validators=[Required()])
        firstname = TextField('Firstname', validators=[Required()])
        fullname = TextField('Fullname')
