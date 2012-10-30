from application import app
from sqlalchemy.ext.hybrid import hybrid_property
from pynuts.model import Orderable


class Company(app.db.Model):
    __tablename__ = 'Company'
    company_id = app.db.Column(app.db.Integer(), primary_key=True)
    name = app.db.Column(app.db.String())
    employees = app.db.relationship(
         'Employee', backref='company', order_by='Employee.order')


class Employee(app.db.Model, Orderable):
    __tablename__ = 'Employee'
    person_id = app.db.Column(app.db.Integer(), primary_key=True)
    name = app.db.Column(app.db.String())
    firstname = app.db.Column(app.db.String())
    login = app.db.Column(app.db.String())
    password = app.db.Column(app.db.String())
    driving_license = app.db.Column(app.db.Boolean())
    resume = app.db.Column(app.db.String())
    photo = app.db.Column(app.db.String())
    order = app.db.Column(app.db.Integer())
    company_id = app.db.Column(
        app.db.Integer(), app.db.ForeignKey('Company.company_id'))

    @hybrid_property
    def fullname(self):
        return '%s %s' % (self.firstname, self.name)
