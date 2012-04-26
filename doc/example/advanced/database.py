from application import app
from sqlalchemy.ext.hybrid import hybrid_property


class Employee(app.db.Model):
        __tablename__ = 'Employee'
        id = app.db.Column(app.db.Integer(), primary_key=True)
        name = app.db.Column(app.db.String())
        firstname = app.db.Column(app.db.String())

        @hybrid_property
        def fullname(self):
            return '%s - %s' % (self.firstname, self.name)
