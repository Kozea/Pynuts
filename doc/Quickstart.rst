Quickstart
==========

A Minimal application
---------------------

A basic Pynuts application is composed of 4 parts:

- An application file instanciating a Flask application
- A view class extended from pynuts ``ModelView``
- A ``SQLAlchemy`` class
- An executable providing routing bewteen endpoints and functions

You can code each part in a specific file to increase readability, but here, one file will work as well.

In this example, we'll see how to create a simple web appliaction allowing you to insert employee records in
database and to list all records.

First, create a file named ``employee.py``::

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
        list_column = 'name'

        class Form(Form):
            id = IntegerField(u'ID', validators=[Required()])
            name = TextField(u'Surname', validators=[Required()])


    #The executable
    @app.route('/')
    def employees():
        return EmployeeView.list('list_employees.html')


    @app.route('add/', methods=('POST', 'GET'))
    def add_employee():
        return EmployeeView().create('add_employee.html',
                                          redirect='employees')

    if __name__ == '__main__':
        app.db.create_all()  # Reflect app models in DB
        app.secret_key = 'Azerty'
        app.run(debug=True, host='127.0.0.1', port=5000)



Following Flask conventions, create a ``templates`` folder, located in the same directory than ``employee.py``.
Then, place the following templates in ``templates/``:

_layout.html
""""""""""""
.. sourcecode:: html+jinja

    <!Doctype html>
    <html>
      <head>
      </head>
      <body>
        <section>
        {% block main %}
        {% endblock main %}
        </section>
      </body>
    </html>

list_employees.html
"""""""""""""""""""
.. sourcecode:: html+jinja

    {% extends "_layout.html" %}

    {% block main %}
      <h2>Employee List</h2>
      {{ view_class.view_list() }}
    {% endblock main %}

add_employee.html
"""""""""""""""""
.. sourcecode:: html+jinja

    {% extends "_layout.html" %}

    {% block main %}
      <h2>Add New Employee</h2>
      {{ view.view_create() }}
    {% endblock main %}


Finally, run the server ::

    $ python employee.py
    * Running on http://127.0.0.1:5000/

Now head over to `http://127.0.0.1:5000/employees/add <http://127.0.0.1:5000/employees/add>`_ to add employees in database, and
`http://127.0.0.1:5000/ <http://127.0.0.1:5000/>`_, to list all employees in database.

So what did that code do?

#. Import what we need to create this small application: Flask (to run a simple WSGI server) and Pynuts.
#. Create a model for an employee, defining how it will be reflected in database.
#. Create a view for an employee
#. Set the ``list_column`` which will define how your employee will be displayed when listed,
#. Create a simple ``WTForms`` form defining the labels of the Employee forms used during basic CRUD functions.
#. At the end of the file, we set the index route for the flask application, create the database and run the server.

To stop the server, hit control-C.

.. seealso::
  `How to run a simple flask application <http://flask.pocoo.org/docs/quickstart/>`_
