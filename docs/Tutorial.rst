Tutorial
========

The first part of this tutorial describes how to implement step-by-step a Pynuts
application granting CRUD operations over a simple data model.

Step 1: Creating the files
--------------------------

Create 4 files at the root of your application:

- application.py
- view.py
- database.py
- executable.py

Then create the `templates` and `static` folders, in the same directory.


Step 2: application.py: defining the Pynuts application
-----------------------------------------------------------

First, import ``pynuts`` by calling::

    import pynuts   

Then, specify its configuration::

    CONFIG = {
        'CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'}
        
.. note::
    
    Refer to the Pynuts `configuration <Configuration.html>`_ page for more information.

Finally, create your pynuts application with the previous configuration

.. sourcecode:: python

    app = pynuts.Pynuts(__name__, config=CONFIG)


.. _hybrid:

Step 3: database.py: the database model
-------------------------------------------

Import the pynuts application::

    from application import app
    from sqlalchemy.ext.hybrid import hybrid_property
    
Then, create a ``SQLAlchemy.Model`` class. 
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


.. note:: 
    
    We decided here to add a ``fullname`` property in our model, being a better
    representative of an employee than simply its name or firstname.
    This property will be especially useful when displaying the employees list.

Step 4: view.py: the view model
-----------------------------------

Import some things from WTForms, the pynuts application and the database model::

    from flask.ext.wtf import Form, TextField, Required

    import database
    from application import app

Create the view class that represents the Employee class. It extends the pynuts ModelView::

    class EmployeeView(app.ModelView):
        

Then, specify the following class attributes: the database model class,::

    model = database.Employee
      
the column representing the class,::

    list_column = 'fullname'
    
.. warning:: 
    ``list_column`` must be a str, not a tuple. It you want to display multiple arttributes for each element of the list,
    use a ``hybrid_property``, as shown in :ref:`hybrid`
    
and the create_columns are the columns displayed in the view. 

::

    create_columns = ('name', 'firstname')

To finish we have to create a form for our view class. The form is extended from the `Flask-WTForms <http://packages.python.org/Flask-WTF>`_ Form.

This form is used for representing the columns from the Employee class into HTML field using WTForms fields. Those fields will be displayed in all CRUD views.
::

    class Form(Form):
        id = IntegerField(u'ID')
        name = TextField(u'Surname', validators=[Required()])
        firstname = TextField(u'Firstname', validators=[Required()])
        fullname = TextField(u'Fullname')


Step 5: The executable
-----------------------

The executable file provides all the routing rules.

In this file you have to import your pynuts application and your database by calling::

    from view import EmployeeView
    from application import app


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
        return view.EmployeeView().create(
            'add_employee.html', redirect='employees')

The Main
~~~~~~~~

::

    if __name__ == '__main__':
        app.db.create_all()
        app.secret_key = 'Azerty'
        app.run(debug=True, host='127.0.0.1', port=5000)

In the main, we initialize the SQLite and then run the server.
Since the application is a Flask one, you have to set a `secret_key` if you want the server to run properly.  

Step 6: The Templates
---------------------

For more information about the templates, you can see the `Jinja2 documentation <http://jinja.pocoo.org/docs/templates>`_

_layout.html
~~~~~~~~~~~~
This template contains the HTML skeleton.

.. literalinclude:: /example/simple/templates/_layout.html
    :language: html+jinja

list_employees.html
~~~~~~~~~~~~~~~~~~~
.. literalinclude:: /example/simple/templates/list_employees.html
    :language: html+jinja

add_employee.html
~~~~~~~~~~~~~~~~~
.. literalinclude:: /example/simple/templates/add_employee.html
    :language: html+jinja

Handling form errors
~~~~~~~~~~~~~~~~~~~~

Handling errors is really simple. Just add this code to your ``_layout.html`` template

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

Create a file `style.css` and paste the following CSS code in it:

.. literalinclude:: /example/simple/static/style.css
    :language: css

------
 
→ `See the tutorial source on GitHub <https://github.com/Kozea/Pynuts/tree/master/docs/example/simple>`_
