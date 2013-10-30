from wtforms import (
    TextField, IntegerField, PasswordField, BooleanField)
from wtforms.ext.sqlalchemy.fields import (
    QuerySelectField, QuerySelectMultipleField)
from wtforms.validators import Required
from . import database
from .application import nuts
from pynuts.fields import UploadField, ImageField
from pynuts.validators import AllowedFile, MaxSize
from pynuts.view import BaseForm
from .files import UPLOAD_SETS


class EmployeeView(nuts.ModelView):
    model = database.Employee

    list_column = 'fullname'
    table_columns = ('order', 'fullname', 'driving_license')
    create_columns = ('login', 'password', 'name', 'firstname', 'company',
                      'resume', 'photo', 'driving_license')
    read_columns = ('person_id', 'name', 'firstname', 'fullname', 'company',
                    'resume', 'photo', 'driving_license')
    update_columns = ('name', 'firstname', 'company', 'driving_license',
                      'resume', 'photo', 'order')

    class Form(BaseForm):
        person_id = IntegerField('ID')
        login = TextField('Login', validators=[Required()])
        password = PasswordField('Password', validators=[Required()])
        name = TextField('Surname', validators=[Required()])
        firstname = TextField('Firstname', validators=[Required()])
        fullname = TextField('Employee name')
        driving_license = BooleanField('Driving license')
        resume = UploadField(
            label='resume',
            upload_set=UPLOAD_SETS['resumes'],
            validators=[AllowedFile(), MaxSize(1)])
        photo = ImageField(
            label='photo',
            upload_set=UPLOAD_SETS['images'],
            validators=[AllowedFile(), MaxSize(1)])
        company = QuerySelectField(
            'Company', get_label='name',
            query_factory=lambda: database.Company.query, allow_blank=True)


class CompanyView(nuts.ModelView):
    model = database.Company

    list_column = 'name'
    create_columns = ('name', 'employees')
    read_columns = ('name', 'employees')

    view_list_template = 'list.jinja2'

    class Form(BaseForm):
        company_id = IntegerField('Company')
        name = TextField('Company name')
        employees = QuerySelectMultipleField(
            'Employees', get_label='fullname', query_factory=
            lambda: database.Employee.query.filter_by(company_id=9999))
