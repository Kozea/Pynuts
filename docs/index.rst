.. Pynuts documentation master file, created by
   sphinx-quickstart on Tue Apr 24 10:37:37 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Pynuts' documentation!
==================================
    
Latest Version: |version|

Pynuts is a Flask extension simplifying the implementation of the generic views of your app.

It allows you to: 
 
- implement and configure `CRUD <https://en.wikipedia.org/wiki/Create,_read,_update_and_delete>`_ view functions in a few lines, using your database schema.
- secure your application by easily managing user permissions using the request context.
- generate HTML and PDF documents containing data from any model instance you created.
- manage different versions of these document with an embedded git repository.
- drastically reduce the amount of code to write and development time by focusing on your application logic and deferring the boring parts to Pynuts.


A create view function, powered by Pynuts
-----------------------------------------
Let’s compare the code you would have to write, without and with Pynuts, in order to implement a basic create view:


Without Pynuts
""""""""""""""

.. code-block:: python
    
    app.route('/employee/add', methods=('GET', 'POST'))
    def add_employee():
        form = EmployeeForm()
        if form.validate_on_submit():
            employee = Employee()
            form.populate_obj(employee)
            db.session.add(employee)
            db.session.commit()
            return redirect(url_for(
                'read_employee', employee_id=employee.employee_id))
        else:
            return render_template(url_for('add_employee'))


With Pynuts
"""""""""""

.. code-block:: python

    @EmployeeView.create_page
    @app.route('/employee/add', methods=('GET', 'POST'))
    def add_employee():
        return EmployeeView().create('create_employee.html.jinja2')


Dependencies
------------

Pynuts is based on

    - `Flask <https://github.com/mitsuhiko/flask>`_
    - `SQLAlchemy <http://www.sqlalchemy.org/>`_
    - `WTForms <http://wtforms.simplecodes.com/>`_
    - `Flask Uploads <http://packages.python.org/Flask-Uploads/>`_
    - `WeasyPrint <http://weasyprint.org/>`_
    - `Git <https://www.samba.org/~jelmer/dulwich/>`_


User's guide
------------

.. toctree::
    :maxdepth: 2

    Installation
    Configuration
    Quickstart
    Tutorial
    Advanced tutorial
    Additional features
    API
