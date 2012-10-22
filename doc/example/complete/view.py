from flask.ext.wtf import (Form, TextField, IntegerField,
                           PasswordField, Required, QuerySelectField,
                           QuerySelectMultipleField, BooleanField)

import database
from application import app


class EmployeeView(app.ModelView):
    model = database.Employee

    list_column = 'fullname'
    table_columns = ('order', 'fullname', 'driving_license')
    create_columns = ('login', 'password', 'name', 'firstname', 'company',
                      'driving_license')
    read_columns = ('person_id', 'name', 'firstname', 'fullname', 'company',
                    'driving_license')
    update_columns = ('name', 'firstname', 'company', 'driving_license', 'order')

    class Form(Form):
        person_id = IntegerField('ID')
        login = TextField(u'Login', validators=[Required()])
        password = PasswordField(u'Password', validators=[Required()])
        name = TextField(u'Surname', validators=[Required()])
        firstname = TextField(u'Firstname', validators=[Required()])
        fullname = TextField('Employee name')
        driving_license = BooleanField('Driving license')
        company = QuerySelectField(
            u'Company', get_label='name',
            query_factory=lambda: database.Company.query, allow_blank=True)


class CompanyView(app.ModelView):
    model = database.Company

    list_column = 'name'
    create_columns = ('name', 'employees')
    read_columns = ('name', 'employees')

    list_template = 'list.jinja2'

    class Form(Form):
        company_id = IntegerField('Company')
        name = TextField('Company name')
        employees = QuerySelectMultipleField(
            u'Employees', get_label='fullname', query_factory=
            lambda: database.Employee.query.filter_by(company_id=9999))
