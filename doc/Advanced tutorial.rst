Advanced tutorial
=================


CRUD
-----------
With advanced pynuts features, you can easily create an admin table which will provide CRUD functions.

First, create a template called ``table_employees.html`` as below:

.. sourcecode:: html+jinja   

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Employees</h2>
      {{ cls.view_table() }}
    {% endblock main %}

This template call the *view_table* function from pynuts, which display a table with your employees and an *edit* and *delete* function for each of them.

Then, you have to call this template in the function *table* in the file ``executable.py``::

    @app.route('/employees/table')
    def table_employees():
        return view.EmployeeView.table('table_employees.html')



Edit employee
~~~~~~~~~~~~~

In your route you have to give the model primary keys in parameters in order to access your employee object. Our table Employee have `id` as primary key. So we can call an `EmployeeView` instance according to an `id`.

Create ``edit_employee.html``:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Edit Employee</h2>
      {{ obj.view_edit() }}
    {% endblock main %}

Then put this code in ``executable.py``::

    @app.route('/employee/edit/<id>', methods=('POST', 'GET'))
    def edit_employee(id):
        return view.EmployeeView(id).edit('edit_employee.html',
                                          redirect='employees')

.. note::
        
    If you want to make this function available from the interface, you have to set the `edit_endpoint` in your view class.
    
    If you didn't, you can call a decorator to automatically set this endpoint according to the route you've created. Just add `@view.EmployeeView.edit_page` before the `@app.route`.
    
    For more information, see the `delete` function below.



Delete employee
~~~~~~~~~~~~~~~
Same as edit, but we decided here to use the decorator to set the endpoint.

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
                                            
View employees
~~~~~~~~~~~~~~
Same as delete and edit.

Create ``view_employee.html``:

.. sourcecode:: html+jinja

    {% extends "_layout.html" %}
    {% block main %}
      <h2>Employee</h2>
      {{ obj.view_object() }}
    {% endblock main %}

Then put this code in ``executable.py``::

    @view.EmployeeView.view_page
    @app.route('/employee/view/<id>')
    def view_employee(id):
        return view.EmployeeView(id).view('view_employee.html')


Document
--------

Edit document
~~~~~~~~~~~~~
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
    - Call the `edit` function with the template and theEmployeeView in parameters
    
::

    @app.route('/employee/edit_template/<id>', methods=('POST', 'GET'))
    def edit_employee_report(id):
        employee = view.EmployeeView(id)
        doc = document.EmployeeDoc
        return doc.edit('edit_employee_template.html',
                        employee=employee)

Render document HTML
~~~~~~~~~~~~~~~~~~~~
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

Generate PDF document
~~~~~~~~~~~~~~~~~~~~~
To get the PDF document, call the `download_pdf` function on a EmployeeDoc instance.

``executable.py``::

    @app.route('/employee/download/<id>')
    def download_employee(id):
        doc = document.EmployeeDoc
        return doc.download_pdf(filename='Employee %s report' % (id),
                                employee=view.EmployeeView(id))

Archive
~~~~~~~


Rights
------
Coming soon...
