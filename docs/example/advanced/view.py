from flask.ext.wtf import (Form, TextField, IntegerField,
                           PasswordField, Required, QuerySelectField,
                           QuerySelectMultipleField)

import database
from application import nuts


class EmployeeView(nuts.ModelView):
    model = database.Employee

    list_column = 'fullname'
    table_columns = ('fullname', )
    create_columns = ('login', 'password', 'name', 'firstname', 'company')
    read_columns = ('person_id', 'name', 'firstname', 'fullname', 'company')
    update_columns = ('name', 'firstname')

    class Form(Form):
        person_id = IntegerField('ID')
        login = TextField(u'Login', validators=[Required()])
        password = PasswordField(u'Password', validators=[Required()])
        name = TextField(u'Surname', validators=[Required()])
        firstname = TextField(u'Firstname', validators=[Required()])
        fullname = TextField('Employee name')
        company = QuerySelectField(
            u'Company', get_label='name',
            query_factory=lambda: database.Company.query, allow_blank=True)


class CompanyView(nuts.ModelView):
    model = database.Company

    list_column = 'name'
    create_columns = ('name', 'employees')
    read_columns = ('name', 'employees')

    class Form(Form):
        company_id = IntegerField('Company')
        name = TextField('Company name')
        employees = QuerySelectMultipleField(
            u'Employees', get_label='fullname', query_factory=
            lambda: database.Employee.query.filter_by(company_id=None))
