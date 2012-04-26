from application import app
import view


@app.route('/')
@app.route('/employees/')
def employees():
    return view.EmployeeView.list('list_employees.html')


@app.route('/employees/table')
def table_employees():
    return view.EmployeeView.table('table_employees.html')


@app.route('/employee/add/', methods=('POST', 'GET'))
def add_employee():
    return view.EmployeeView().create('add_employee.html',
                                      redirect='employees')


@view.EmployeeView.edit_page
@app.route('/employee/edit/<id>', methods=('POST', 'GET'))
def edit_employee(id):
    return view.EmployeeView(id).edit('edit_employee.html',
                                      redirect='employees')


@view.EmployeeView.view_page
@app.route('/employee/view/<id>', methods=('POST', 'GET'))
def view_employee(id):
    return view.EmployeeView(id).view('view_employee.html')


@view.EmployeeView.delete_page
@app.route('/employee/delete/<id>', methods=('POST', 'GET'))
def delete_employee(id):
    return view.EmployeeView(id).delete('delete_employee.html',
                                        redirect='employees')


if __name__ == '__main__':
    app.db.create_all()
    app.secret_key = 'Azerty'
    app.run(debug=True, host='127.0.0.1', port=5000)
