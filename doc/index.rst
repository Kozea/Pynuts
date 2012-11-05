.. Pynuts documentation master file, created by
   sphinx-quickstart on Tue Apr 24 10:37:37 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Pynuts' documentation!
==================================
    
Latest Version: 0.1

Pynuts is a Flask extension which will simplify your code by creating some generic content.

It allows you to: 
 
 - implement some basic CRUD (Create, Read, Update and Delete) view functions for administration in a few lines.
 - secure your application by easily manage permissions using the request context.
 - handle HTML and PDF documents with git, you can store anything you want for any instance you created.
   Of course, you can use all the features that git provides and do what you want with your documents, that's why Pynuts is a powerful tool for developpers.
 - drastically reduce the amount of code to write.

Have a look at this comparison:

.. table::
    :class: compare-table

    +---------------------------------------------------------------------+-------------------------------------------------------------------------------------+
    | Without Pynuts:                                                     |  With Pynuts:                                                                       |
    +=====================================================================+=====================================================================================+
    | .. sourcecode:: python                                              | .. sourcecode:: python                                                              |
    |                                                                     |                                                                                     |
    |                                                                     |     @EmployeeView.create_page                                                       |
    |    @app.route('/employee/add', methods=('GET', 'POST'))             |     @app.route('/employee/add', methods=('GET', 'POST'))                            |
    |    def add_employee():                                              |     def add_employee():                                                             |
    |        form = EmployeeForm()                                        |         return EmployeeView().create('create_employee.html.jinja2')                 |
    |        if form.validate_on_submit():                                |                                                                                     |
    |            employee = Employee()                                    |                                                                                     |
    |            form.populate_obj(employee)                              |                                                                                     |
    |            db.session.add(employee)                                 |                                                                                     |
    |            db.session.commit()                                      |                                                                                     |
    |            return redirect(url_for(                                 |                                                                                     |
    |                'read_employee', employee_id=employee.employee_id))  |                                                                                     |
    |        else:                                                        |                                                                                     |
    |            return render_template(url_for('add_employee'))          |                                                                                     |
    |                                                                     |                                                                                     |
    +---------------------------------------------------------------------+-------------------------------------------------------------------------------------+

Pynuts is based on

    - `Flask <https://github.com/mitsuhiko/flask>`_
    - `SQLAlchemy <http://www.sqlalchemy.org/>`_
    - `WTForms <http://wtforms.simplecodes.com/>`_
    - `Flask Uploads <http://packages.python.org/Flask-Uploads/>`_
    - `WeasyPrint <http://weasyprint.org/>`_
    - `Git <https://www.samba.org/~jelmer/dulwich/>`_


Contents:
---------

.. toctree::
    :maxdepth: 2

    Installation
    Quickstart
    Tutorial
    Advanced tutorial
    Additional features
    Configuration
    API
