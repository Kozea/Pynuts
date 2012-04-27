Advanced tutorial
=================


Admin table
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

::

    @app.route('/employee/edit/<id>', methods=('POST', 'GET'))
    def edit_employee(id):
        return view.EmployeeView(id).edit('edit_employee.html',
                                          redirect='employees')

.. note::
        
    If you want to make this function available from the interface, you have to set the `edit_endpoint` in your view class.
    
    If you didn't, you can call a decorator to automatically set this endpoint according to the route you created. Just add `@view.EmployeeView.edit_page` before the `@app.route`. See the `delete` function below.



Delete employee
~~~~~~~~~~~~~~~
Same as edit, but we decided here to use the decorator to set the endpoint.
::

    @view.EmployeeView.delete_page
    @app.route('/employee/delete/<id>')
    def delete_employee(id):
        return view.EmployeeView(id).delete('delete_employee.html',
                                            redirect='employees')
                                            
View employees
~~~~~~~~~~~~~~
Same as delete and edit.

::

    @view.EmployeeView.view_page
    @app.route('/employee/view/<id>')
    def view_employee(id):
        return view.EmployeeView(id).view('view_employee.html')


Document
--------

Edit template
~~~~~~~~~~~~~

Render document HTML
~~~~~~~~~~~~~~~~~~~~

Generate PDF document
~~~~~~~~~~~~~~~~~~~~~

The templates
-------------
