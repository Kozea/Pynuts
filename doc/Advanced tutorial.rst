Advanced tutorial
=================


CRUD
------
The CRUD part is explained in the first tutorial. 


Table of Employees
~~~~~~~~~~~~~~~~~~

With advanced pynuts features, you can easily create an admin table which will provide CRUD operations over a data model.

First, create a template called ``table_employees.html``:

.. sourcecode:: html+jinja   

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Employees</h2>
      {{ view_class.view_table() }}
    {% endblock main %}

This template calls the ``view_table`` method from pynuts, which display a table containing all employees and an `edit` and `delete` method for each of them.

Then, use this template as argument of the ``EmployeeView.table`` method in ``executable.py``::

    @app.route('/employees/table')
    def table_employees():
        return view.EmployeeView.table('table_employees.html')


.. _update:

Update Employee
~~~~~~~~~~~~~~~

You need to pass the model primary keys as route parameters in order to have access to an employee object.
The primary key of the Employee table is ``id``, so we can call an `EmployeeView` instance according to an `id`.

Create ``update_employee.html``:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Update Employee</h2>
      {{ view.view_update() }}
    {% endblock main %}

Add this function in ``executable.py``::

    @view.EmployeeView.update_page
    @app.route('/employee/update/<id>', methods=('POST', 'GET'))
    def update_employee(id):
        return view.EmployeeView(id).update(
            'update_employee.html', redirect='employees')

.. note::
        
    If you want to make this function available from the interface, you have to set the `update_endpoint` in your view class.
    
    If you do not, you can call a decorator to automatically set this endpoint according to the route you've created. Just add `@view.EmployeeView.update_page` before the `@app.route`.
    
    For more information, see the `delete` function below.


.. _delete:

Delete Employee
~~~~~~~~~~~~~~~
The logic here is the same than in :ref:`update`.

First, create the ``delete_employee.html`` template:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Delete Employee</h2>
      {{ view.view_delete() }}
    {% endblock main %}

    
The, add this function in ``executable.py``::

    @view.EmployeeView.delete_page
    @app.route('/employee/delete/<id>')
    def delete_employee(id):
        return view.EmployeeView(id).delete(
            'delete_employee.html', redirect='employees')
                                            
Read Employee
~~~~~~~~~~~~~
The logic here is the same than in :ref:`update` and :ref:`delete`.

Create the ``read_employee.html`` template:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Employee</h2>
      {{ view.view_read() }}
    {% endblock main %}

Add this function in ``executable.py``::

    @view.EmployeeView.read_page
    @app.route('/employee/read/<id>')
    def read_employee(id):
        return view.EmployeeView(id).read('read_employee.html')


Document
--------


This part describes how to create documents, manage them using a version control system and convert these HTML documents into PDF reports.


Configuration
~~~~~~~~~~~~~
If you want to use document archiving, you need to add the path to your document repository in the application config. 
Go to ``application.py`` and add this ``'PYNUTS_DOCUMENT_REPOSITORY'`` as key to the CONFIG then put the path to the `repo.git`; In this tutorial we have `/tmp/employees.git` as value.

Refer to the Pynuts `configuration <Configuration.html>`_ page for more information.
    
    
Creating Our Document Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start by creating the file ``document.py`` which will contain the Pynuts document class. 

::

    from application import app


    class EmployeeDoc(app.Document):
        model_path = 'models/'
        document_id_template = '{employee.data.id}'


`model_path` 
The path to the folder where the model is stored. You have to create a file named `index.rst.jinja2` in this folder, this will be your document template written in ReST/Jinja2.

`document_id_template`
 In this tutorial the document_id_template is the employee id.


Creating Documents
~~~~~~~~~~~~~~~~~~

We would like to create an Employee document each time an employee is succesfully added into database.
To do so, go back to the *create* route in ``executable.py`` and insert the following snippet

::

  @app.route('/employee/create/', methods=('POST', 'GET'))
  def create_employee():
      employee = view.EmployeeView()
      response = employee.create(
          'create_employee.html', redirect='employees')
      if employee.create_form.validate_on_submit():
          document.EmployeeDoc.create(employee=employee)
      return response

This function performs the following operations:

- Create an instance of EmployeeView
- Call the create method of EmployeeView. 
- Create a new document, if the employee `create_form` is validated.
- Finally, redirect to the list of employees

When the document is created for the first time, Pynuts make an initial commit of the folder which contains the model in a new branch. 

.. note ::
    
    ``create_form`` is the form generated by pynuts according to the value of ``create_columns`` you specified. See the :ref:`api` documentation for more info.
    

Editing Document
~~~~~~~~~~~~~~~~
Now that the document has been created, you may want to edit it and add some information for one specific employee.
Pynuts document handling makes these operations very simple to perform.

Create the file ``edit_employee_template.html``

.. sourcecode:: html+jinja

    % extends "_layout.html" %}
    {% block main %}
      {{ document.view_edit(employee=employee) }}
    {% endblock main %}


Then, insert the following snippet in ``executable.py``
    
::

    @app.route('/employee/edit_template/<id>', methods=('POST', 'GET'))
    def edit_employee_report(id):
        employee = view.EmployeeView(id)
        doc = document.EmployeeDoc
        return doc.edit(
            'edit_employee_template.html', employee=employee)

This function performs the following operations:

  - Declare an EmployeeView
  - Declare an EmployeeDoc
  - Call the `edit` function with the template and the EmployeeView in parameters

Rendering Document in HTML
~~~~~~~~~~~~~~~~~~~~~~~~~~
Create the``employee_report.html`` template:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      {{ document.view_html(employee=employee) }}
    {% endblock main %}

and add this snippet to ``executable.py``::

    @app.route('/employee/html/<id>', methods=('POST', 'GET'))
    def html_employee(id):
        doc = document.EmployeeDoc
        return doc.html('employee_report.html', employee=view.EmployeeView(id))

Download PDF Document
~~~~~~~~~~~~~~~~~~~~~
To download the PDF version of the document, call the ``download_pdf`` class method of a EmployeeDoc in ``executable.py``::

    @app.route('/employee/download/<id>')
    def download_employee(id):
        doc = document.EmployeeDoc
        return doc.download_pdf(
            filename='Employee %s report' % (id), employee=view.EmployeeView(id))


Working with versions
~~~~~~~~~~~~~~~~~~~~~

Get the version list
````````````````````

To all the existing versions of the archived document, use the ``history`` property of a document instance. 
We can create an instance by giving the id of an employee which is also the id of the document.

::
  
    history = document.EmployeeDoc(id).history 
    
Then we have to return the read template with the list of versions::

    return view.EmployeeView(id).read('read_employee.html', history=history)
    
Now go to the ``read_employee.html`` template. To use ``history``, we loop on it and each element is a `EmployeeDoc` instance.
So we can use the instance properties like the version of the document. 

In the following example, we generate a table:

#. The first column contains the document datetime by using the `datetime` property of `EmployeeDoc`. 
#. The second column contains the commit message.
#. The third column contains a link allowin to edit the archived template
#. The fourth columns contains a link to view the html of the template
#. The fifth column contains a link to the pdf download

.. sourcecode:: html+jinja

  {% extends "_layout.html" %}

  {% block main %}
    <h2>Employee</h2>
    {{ view.view_read() }}

    <h2>Document history</h2>
    <table>
      <tr>
        <th>Commit datetime</th>
        <th>Commit message</th>
        <th>Edit</th>
        <th>HTML</th>
        <th>PDF</th>
      </tr>
      {% for archive in history %}
        <tr>
          <th>{{ archive.datetime }}</th>
          <td>{{ archive.message }}</td>
          <td><a href="{{ url_for('edit_employee_report', version=archive.version, **view.primary_keys) }}">></a></td>
          <td><a href="{{ url_for('html_employee', version=archive.version, **view.primary_keys) }}">></a></td>
          <td><a href="{{ url_for('pdf_employee', version=archive.version, **view.primary_keys) }}">></a></td>
        </tr>
      {% endfor %}
    </table>
  {% endblock main %}

I hope you noticed that the ``edit_employee_report``, ``html_employee`` and ``pdf_employee`` view functions already exist. You just have to add a new route to those view function which takes the version in parameter. 
Something like that for the `html_employee` view::

    @app.route('/employee/html/<id>')
    @app.route('/employee/html/<id>/<version>')
    def html_employee(id, version=None):
        doc = document.EmployeeDoc
        return doc.html(
            'employee_report.html', employee=view.EmployeeView(id), version=version)
                        
Finally, go back to the ``edit_employee_template.html`` template in order to add the version in parameter of the view classmethod of `EmployeeDoc`

.. sourcecode:: html+jinja
 
    {% block main %}
      {{ document.view_edit(employee=employee, version=version) }}
    {% endblock main %}
    
Do the same with ``employee_report.html``.

Now you can run the server and see that everything runs smoothly!

Rights
------
With pynuts, setting specific permissions on each endpoint is quite simple. First, create a ``rights.py`` file . In this file, import your app and the ``rights`` module::

  from application import app
  from pynuts.rights import acl
 
Then, create a `Context` class, inheriting from your application context. Here you can define some properties that will be used for the context of your rights.

For example, we decided here to create a property called `person` which will stands for the current logged on user::

    class Context(app.Context):
    
        @property
        def person(self):
            """Returns the current logged on person, or None."""
            return session.get('id')
            
Once you're done with the context class, you can create your own rights thanks to the ACL you imported above. The ACL class is an utility decorator for access control in `allow_if` decorators. The `allow_if` decorator check that the global context matches a criteria.

The context is stored in the `g <http://flask.pocoo.org/docs/api/#flask.g>`_ object of your application.

Your functions should look like the following one ::

    @acl
    def connected():
        """Returns whether the user is connected."""
        return g.context.person is not None
        
Then, import your rights in the file ``executable.py`` along with the `allow_if` function from `pynuts.rights`.
You can import rights as `Is` to have a good syntax using the allow_if decorator: ``@allow_if(Is.connected)`` for example.

All you have to do now is to put a decorator before your function to apply rights::

    @app.route('/employees/')
    @allow_if(Is.connected)
    def employees():
        return view.EmployeeView.list('list_employees.html')

Here, the access to the list of employees won't be granted if you aren't connected.

Of course, you can combine some rights, it implements the following operators:

+-------+---------+
| a & b | a and b |
+-------+---------+
| a | b | a or b  |
+-------+---------+
| a ^ b | a xor b |
+-------+---------+
|  ~ a  |  not a  |
+-------+---------+
    
You can write this for example: 

``@allow_if((Is.connected & ~Is.blacklisted) | Is.admin)``

This will grant the access for a connected person which isn't blacklisted or to the admin.


Help
~~~~
You need help with this tutorial ? The full source code is available on Github `here <https://github.com/Kozea/Pynuts/tree/master/doc/example/advanced>`_.

Something doesn't work ? You want a new feature ? Feel free to write some bug report or feature request on the `issue tracker <http://redmine.kozea.fr/projects/pynuts>`_.
