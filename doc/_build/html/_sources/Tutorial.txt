Tutorial
========

The first part of this tutorial describes how to basically make CRUD with a Pynuts application. 
The second part explains 

Step 1: Creating the files
--------------------------

Create 4 files at the root of your application:

- application.py
- view.py
- database.py
- executable.py

Then create the `templates` and `static` folders.


Step 2: Defining the Pynuts application
---------------------------------------

First, in ``application.py`` you have to import pynuts module by calling::

    import pynuts   

Then you have to specify the configuration like this::

    CONFIG = {
        'CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'}
        
`CSRF_ENABLED`
    This is used by WTForms, see `WTForms documentation <http://packages.python.org/Flask-WTF>`_
    
`SQLALCHEMY_DATABASE_URI` 
    This is the database. In this tutorial we will use a SQLite database.

Finally you have to create your pynuts application with the configuration written before::

    app = pynuts.Pynuts(__name__, config=CONFIG)


Step 3: The database model
--------------------------

In ``database.py`` import the pynuts application::

    from application import app
    from sqlalchemy.ext.hybrid import hybrid_property
    
Then, create a SQLAlchemy class. 
`Learn more about SQLAlchemy <http://www.sqlalchemy.org>`_

::

    class Employee(app.db.Model):
        __tablename__ = 'Employee'
        id = app.db.Column(app.db.Integer(), primary_key=True)
        name = app.db.Column(app.db.String())
        firstname = app.db.Column(app.db.String())

        @hybrid_property
        def fullname(self):
            return '%s - %s' % (self.firstname, self.name)

We decided here to add a property in our model called `fullname`, which represents better the employee than a simple name or firstname.

It will be useful to easily display the employees' list later.

Step 4: The view model
----------------------

In ``view.py`` you have to import some things from WTForms, the pynuts application and the database model::

    from flaskext.wtf import Form, TextField, Required

    import database
    from application import app

Now you have to create the view class that represents the Employee class. It extends the pynuts ModelView::

    class EmployeeView(app.ModelView):
        

Then you have to specify the class attributes.

Our database model class::

    model = database.Employee
      
The column which represents the class::

    list_column = 'fullname'
    
*Warning : This must be a String not a Tuple*
    
The create_columns are the columns displayed in the view. 

::

    create_columns = ('name', 'firstname')

To finish we have to create a form for our view class. The form is extended form the Flask-WTForms Form.
See `Flask-WTForms <http://packages.python.org/Flask-WTF>`_ for more information.

This form is used for representing the columns from the Employee class into HTML field using WTForms fields. Those fields will be displayed in CRUD views.
::

    class Form(Form):
        name = TextField(u'Surname', validators=[Required()])
        firstname = TextField(u'Firstname', validators=[Required()])


Step 5: The executable
-----------------------

The executable file provides all the routes.

In this file you have to import your pynuts application and your database by calling::


    from application import app
    from pynuts import view

The List View
~~~~~~~~~~~~~

All the employees are listed in this view.
To list them we call the method `list` which takes the template name as first parameter.

::

    @app.route('/')
    @app.route('/employees/')
    def employees():
        return view.EmployeeView.list('list_employees.html')


The Add View
~~~~~~~~~~~~

This view allows the `POST` and `GET` methods. The `POST` one is used for adding a new entry in the database. The `GET` one is used for displaying the create form acording to the `create_columns` you specified in ``view.py``. The method create takes the template as first parameter and the view returned if the adding went well as second parameter. In our turorial we redirect to the list view.

::

    @app.route('/employee/add/', methods=('POST', 'GET'))
    def add_employee():
        return view.EmployeeView().create('add_employee.html',
                                          redirect='employees')

The Main
~~~~~~~~

The main looks like that::

    if __name__ == '__main__':
        app.db.create_all()
        app.secret_key = 'Azerty'
        app.run(debug=True, host='127.0.0.1', port=5000)

In the main, we initialize the SQLite database and then run the server.
Since the application is a Flask one, you have to set a `secret_key` if you want the server to run properly.  

Step 6: The Templates
---------------------

For more information about the templates, you can see the `Jinja2 documentation <http://jinja.pocoo.org/docs/templates>`_

layout.html
~~~~~~~~~~~
This template contains the HTML skeleton.

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
~~~~~~~~~~~~~~~~~~~
This template show a list of all employees present in the database.

`cls` stands for the EmployeeView class.

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}

    {% block main %}
      <h2>Employee List</h2>
      {{ cls.view_list() }}
    {% endblock main %}
    
add_employee.html
~~~~~~~~~~~~~~~~~

This template shows a form to create an employee.

`obj` stands_for an instance of EmployeeView.

.. sourcecode:: html+jinja
    
    {% extends "_layout.html" %}

    {% block main %}
      <h2>Add New Employee</h2>
      {{ obj.view_create() }}
    {% endblock main %}

Handling form errors
~~~~~~~~~~~~~~~~~~~~

Handling errors is really simple. Just add this code to your ``layout.html``

.. sourcecode:: html+jinja

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% for style, messages in messages | groupby(0) %}
        <aside class="{{ style }}">
          <ul>
            {% for message in messages %}
              <li>{{ message[1] }}</li>
            {% endfor %}
          </ul>
        </aside>
      {% endfor %}
    {% endwith %}

Step 7: Adding Style
--------------------
The final step to your little application. Everything should be working fine, it's time to add some style !

Create a file `style.css` in the static folder, you can use the css below:

.. sourcecode:: css

    body            { font-family: sans-serif; background: #eee;
                        margin: 0; padding: 0; width: 80%; margin-left: 10%; }
    a, h1, h2       { color: #377BA8; }
    h1, h2          { font-family: 'Georgia', serif; margin: 0; }
    h1              { border-bottom: 2px solid #eee; text-align: center; }
    h2              { font-size: 1.2em; }

    nav             { text-align: center; margin: 1em; }
    nav a           { margin: 1em; }

    section         { border: 1px solid #ddd; }

    form            { margin: 0.5em; }

    .error ul       { background: #F0D6D6; }

------
 
-> `Get the whole tutorial application <https://github.com/Kozea/Pynuts>`_
