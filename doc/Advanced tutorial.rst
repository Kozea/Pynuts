Advanced tutorial
=================


CRUD
------
The CRUD part is explained in the first tutorial. 


Table of Employees
~~~~~~~~~~~~~~~~~~

With advanced pynuts features, you can easily create an admin table which will provide CRUD functions.

First, create a template called ``table_employees.html`` as below:

.. sourcecode:: html+jinja   

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Employees</h2>
      {{ cls.view_table() }}
    {% endblock main %}

This template call the `view_table` method from pynuts, which display a table with your employees and an `edit` and `delete` method for each of them.

Then, you have to call this template in the function `table` in the file ``executable.py``::

    @app.route('/employees/table')
    def table_employees():
        return view.EmployeeView.table('table_employees.html')



Update Employee
~~~~~~~~~~~~~~~

In your route you have to give the model primary keys in parameters in order to access your employee object. Our table Employee have `id` as primary key. So we can call an `EmployeeView` instance according to an `id`.

Create ``update_employee.html``:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Update Employee</h2>
      {{ obj.view_update() }}
    {% endblock main %}

Then put this code in ``executable.py``::

    @view.EmployeeView.update_page
    @app.route('/employee/update/<id>', methods=('POST', 'GET'))
    def update_employee(id):
        return view.EmployeeView(id).update('update_employee.html',
                                          redirect='employees')

.. note::
        
    If you want to make this function available from the interface, you have to set the `update_endpoint` in your view class.
    
    If you didn't, you can call a decorator to automatically set this endpoint according to the route you've created. Just add `@view.EmployeeView.update_page` before the `@app.route`.
    
    For more information, see the `delete` function below.



Delete Employee
~~~~~~~~~~~~~~~
Same as update.

Create ``delete_employee.html``:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Delete Employee</h2>
      {{ obj.view_delete() }}
    {% endblock main %}

    
Then put this code in ``executable.py``::

    @view.EmployeeView.delete_page
    @app.route('/employee/delete/<id>')
    def delete_employee(id):
        return view.EmployeeView(id).delete('delete_employee.html',
                                            redirect='employees')
                                            
Read Employee
~~~~~~~~~~~~~
Same as delete and update.

Create ``read_employee.html``:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Employee</h2>
      {{ obj.view_read() }}
    {% endblock main %}

Then put this code in ``executable.py``::

    @view.EmployeeView.read_page
    @app.route('/employee/read/<id>')
    def read_employee(id):
        return view.EmployeeView(id).read('read_employee.html')


Document
--------


This part will describe how to make documents, make version and generate beautiful PDF report with Pynuts.


Configuration
~~~~~~~~~~~~~
If you want to use document archiving, you need to add the path to your document repository in the application config. Go to ``application.py`` and add this `'PYNUTS_DOCUMENT_REPOSITORY'` as key to the CONFIG then put the path to the `repo.git`; In this tutorial we have `/tmp/employees.git` as value.
Now you have to make the repo. 

 
Git Repository
~~~~~~~~~~~~~~

Simply create a bare git repository.

::

    $ git init --bare /tmp/employees.git
    
    
Creating Our Document Class
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start by creating the file ``document.py`` which will contain the Pynuts document class. 

::

    from application import app


    class EmployeeDoc(app.Document):
        model_path = 'models/'
        document_id_template = '{employee.data.id}'


`model_path` 
 That's the path to the folder where the model is stored. You have to create a file named `index.rst.jinja2` in this folder, this will be your document template written in ReST/Jinja2.

`document_id_template`
 In this tutorial the document_id_template is the employee id.


Creating Documents
~~~~~~~~~~~~~~~~~~

When an employee is added in database and everything went well, we create an employee document.
So you have to go back to the *create* route in ``executable.py``.

- First create an instance of EmployeeView
- Then we call the create method of EmployeeView. 
- If the employee `create_form` is validated we create a new document.
- Finally we redirect to the list of employees

::

  @app.route('/employee/create/', methods=('POST', 'GET'))
  def create_employee():
      employee = view.EmployeeView()
      response = employee.create('create_employee.html',
                                 redirect='employees')
      if employee.create_form.validate_on_submit():
          document.EmployeeDoc.create(employee=employee)
      return response

When the document is created for the first time, Pynuts make an initial commit of the folder which contains the model in a new branch. 

.. note ::
    
    create_form is the form made by pynuts according to `create_columns` you have specified. See the :ref:`api` documentation for more info.
    

Editing Document
~~~~~~~~~~~~~~~~
Since the document has been created, you may want to edit it and add some information for one specific employee.

Thanks to pynuts document handling, it's possible and quite easy to do.

Create the file ``edit_employee_template.html``

.. sourcecode:: html+jinja

    % extends "_layout.html" %}
    {% block main %}
      {{ cls.view_edit(employee=employee) }}
    {% endblock main %}

Then, in your ``executable.py``, you have to:
    - Declare an EmployeeView
    - Declare an EmployeeDoc
    - Call the `edit` function with the template and the EmployeeView in parameters
    
::

    @app.route('/employee/edit_template/<id>', methods=('POST', 'GET'))
    def edit_employee_report(id):
        employee = view.EmployeeView(id)
        doc = document.EmployeeDoc
        return doc.edit('edit_employee_template.html',
                        employee=employee)

Rendering Document in HTML
~~~~~~~~~~~~~~~~~~~~~~~~~~
Create the file ``employee_report.html``:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      {{ cls.view_html(employee=employee) }}
    {% endblock main %}

``executable.py``::

    @app.route('/employee/html/<id>', methods=('POST', 'GET'))
    def html_employee(id):
        doc = document.EmployeeDoc
        return doc.html('employee_report.html', employee=view.EmployeeView(id))

Getting PDF Document
~~~~~~~~~~~~~~~~~~~~
To get the PDF document, call the `download_pdf` class method of a EmployeeDoc.

``executable.py``::

    @app.route('/employee/download/<id>')
    def download_employee(id):
        doc = document.EmployeeDoc
        return doc.download_pdf(filename='Employee %s report' % (id),
                                employee=view.EmployeeView(id))


Using versions
~~~~~~~~~~~~~~

Get the version list
````````````````````
In our view of an employee we decide to allow the user to access the version of the employee model description.
Go back to the `read_employee` function. In the view of an employee we want to list all the existing versions of the archived document. To list them we just use the `history` property of a document instance. We create an instance by giving the `id` of an employee  which is also the id of the document.

::
  
    history = document.EmployeeDoc(id).history 
    
Then we have to return the read template with the list of versions::

    return view.EmployeeView(id).read('read_employee.html', history=history)
    
Now go to ``read_employee.html``. To use `history`, we loop on it and each element is a `EmployeeDoc` instance. So we can use the instance properties like the version of the document. In this example we make a table:

1. The first column displays the document datetime by using the `datetime` property of `EmployeeDoc`. 
2. This is the commit message.
3. The second create a link to edit the archived template by giving the version to `url_for`.
4. The third create a link to view the html of the template
5. The fourth create a link to the pdf download

.. sourcecode:: html+jinja

  {% extends "_layout.html" %}

  {% block main %}
    <h2>Employee</h2>
    {{ obj.view_read() }}
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
          <td><a href="{{ url_for('edit_employee_report', version=archive.version, **obj.primary_keys) }}">></a></td>
          <td><a href="{{ url_for('html_employee', version=archive.version, **obj.primary_keys) }}">></a></td>
          <td><a href="{{ url_for('pdf_employee', version=archive.version, **obj.primary_keys) }}">></a></td>
        </tr>
      {% endfor %}
    </table>
  {% endblock main %}

I hope you noticed that the `edit_employee_report`, `html_employee` and `pdf_employee` view functions already exists. You just have to add a new route to those view function which takes the version in parameter. Something like that for the `html_employee` view::

    @app.route('/employee/html/<id>')
    @app.route('/employee/html/<id>/<version>')
    def html_employee(id, version=None):
        doc = document.EmployeeDoc
        return doc.html('employee_report.html',
                        employee=view.EmployeeView(id),
                        version=version)
                        
Finally you have to go back to ``edit_employee_template.html`` in order to add the version in parameter of the view classmethod of `EmployeeDoc`

.. sourcecode:: html+jinja
 
    {% block main %}
      {{ cls.view_edit(employee=employee, version=version) }}
    {% endblock main %}
    
Do the same with ``employee_report.html``.

Now you can run the server and see that works perfectly!

Rights
------
With pynuts, putting specific rights for the route you want is quite simple. First, you have to create a file ``rights.py``. In this file, you have to import two major things:
 - Your application `from application import app`
 - The pynuts ACL class `from pynuts.rights import acl`
 
Then, create a `Context` class, inheriting from your application context. Here you can define some properties that will be used for the context of your rights.

For example, we decided here to create a property called `person` which will stands for the current logged on user::

    class Context(app.Context):
    
        @property
        def person(self):
            """Returns the current logged on person, or None."""
            return session.get('id')
            
Once you're done with the context class, you can create your own rights thanks to the ACL you imported above. The ACL class is an utility decorator for access control in `allow_if` decorators. The `allow_if` decorator check that the global context matches a criteria.

Your functions should look like the following::

    @acl
    def connected():
        """Returns whether the user is connected."""
        return app.context.person is not None
        
Then, import your rights in the file ``executable.py`` along with the `allow_if` function from `pynuts.rights` . You can import rights as `Is` to have a good syntax using the allow_if decorator: ``@allow_if(Is.connected)`` for example.

All you have to do now is to put a decorator before your function to apply rights::

    @app.route('/employees/')
    @allow_if(Is.connected)
    def employees():
        return view.EmployeeView.list('list_employees.html')

Here, the access to the list of employees won't be granted if you aren't connected.

Of course, you can combine some rights, it implements the following operators:

+-------+--------+
| a & b | a and b|
+-------+--------+
| a | b | a or b |
+-------+--------+
| a ^ b | a xor b|
+-------+--------+
|  ~ a  |  not a |
+-------+--------+
    
You can write this for example: 

``@allow_if((Is.connected & ~Is.blacklisted) | Is.admin)``

This will grant the access for a connected person which isn't blacklisted or to the admin.

Miscellaneous
-------------

You need help with this tutorial ? The full source code is available on Github `here <https://github.com/Kozea/Pynuts/tree/master/doc/example/advanced>`_.

Something doesn't work ? You want a new feature ? Feel free to write some bug report or feature request on the `issue tracker <http://redmine.kozea.fr/projects/pynuts>`_.
