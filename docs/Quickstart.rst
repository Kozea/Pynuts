Quickstart
==========

In this example, we'll see how to create a simple web appliaction allowing you to insert employee records in
database and to list all records.

A Minimal application
---------------------

A basic Pynuts application is composed of 4 parts:

- An application file instanciating a Flask application
- A view class extended from pynuts generic ``ModelView``
- A ``SQLAlchemy`` class providing an ORM bewteen the pynuts models and the database tables
- An executable providing routing bewteen endpoints and functions

.. note::

        You can code each part in a specific file to improve readability, but here, one file will work as well.


First, create a file named ``employee.py``.

.. literalinclude:: /example/quickstart/employee.py
    :language: python



Following Flask conventions, create a ``templates`` folder, located in the same directory than ``employee.py``.
Then, place the following templates in ``templates/``:

_layout.html
""""""""""""
.. literalinclude:: /example/quickstart/templates/_layout.html
    :language: html+jinja

list_employees.html
"""""""""""""""""""
.. literalinclude:: /example/quickstart/templates/list_employees.html
    :language: html+jinja

add_employee.html
"""""""""""""""""
.. literalinclude:: /example/quickstart/templates/add_employee.html
    :language: html+jinja


Finally, run the server

.. sourcecode:: bash

    $ python employee.py
    * Running on http://127.0.0.1:5000/
    * Restarting with reloader

Now head over to `http://127.0.0.1:5000/ <http://127.0.0.1:5000/>`_, to list all employees in database an to `http://127.0.0.1:5000/employees/add <http://127.0.0.1:5000/employees/add>`_ to insert an employee into the database.

So what did our code do?

#. Import what we need to create this small application: Flask (to run a simple WSGI server) and Pynuts.
#. Instanciate and configure a Flask application.
#. Associate a SQLAchemy ORM object to it.
#. Instanciate a Pynuts object based on our Flask application.
#. Create a model for an employee, defining how it will be reflected in database.
#. Create a view for an employee
#. Set the ``list_column`` which will define how your employee will be displayed when listed,
#. Create a simple ``WTForms`` form defining the labels of the Employee forms used during basic CRUD functions.
#. At the end of the file, we set the index route for the flask application, create the database and run the server.

To stop the server, hit control-C.

→ `See the quickstart source on GitHub <https://github.com/Kozea/Pynuts/tree/master/docs/example/quickstart>`_


.. seealso::
  `How to run a simple flask application <http://flask.pocoo.org/docs/quickstart/>`_
