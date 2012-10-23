Quickstart
==========

A Minimal application
---------------------

A basic Pynuts application requires 4 parts:

- An application file instanciating a Flask application
- A view class extended from pynuts ``ModelView``
- A ``SQLAlchemy`` class
- An executable

You can code each part in a secific file if you want more readability, but here, one file will work as well.

Create a file named ``employee.py``::

    import flask
    from flask.ext.wtf import Form, TextField, IntegerField, Required

    import pynuts

    #The application
    CONFIG = {
        'CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'}

    app = pynuts.Pynuts(__name__, config=CONFIG)


    #The database
    class Employee(app.db.Model):
        __tablename__ = 'Employee'
        id = app.db.Column(app.db.Integer(), primary_key=True)
        name = app.db.Column(app.db.String())


    #The view
    class EmployeeView(app.ModelView):
        model = Employee

        view_columns = ('id', 'name')

        class Form(Form):
            id = IntegerField(u'ID', validators=[Required()])
            name = TextField(u'Surname', validators=[Required()])


    #The executable
    @app.route('/')
    def employees():
        return EmployeeView.list('list_employees.html')

    if __name__ == '__main__':
        app.db.create_all()
        app.secret_key = 'Azerty'
        app.run(debug=True, host='127.0.0.1', port=5000)



Then run the server ::

    $ python employee.py
    * Running on http://127.0.0.1:5000/

Now head over to http://127.0.0.1:5000/, and you should see your list of employees.

So what did that code do?

    First, we import what we need to do a small application : Flask and Pynuts. In fact, we need a flask application to run a simple WSGI server. Then, we create a view for an employee, setting the view_column which will define how your employee will be seen in the application and a simple WTForms form for the basic CRUD functions. We create the database, according to the form we just wrote in the view and it's almost done.
    At the end of the file we set the index route for the flask application, create the database and run the server.

To stop the server, hit control-C.

.. seealso::
  `How to run a simple flask application <http://flask.pocoo.org/docs/quickstart/>`_
