import flask

from application import app
import view
import document


@app.route('/')
@app.route('/employees/')
def employees():
    return view.EmployeeView.list('list_employees.html')


@app.route('/employees/table')
def table_employees():
    return view.EmployeeView.table('table_employees.html')


@app.route('/employee/add/', methods=('POST', 'GET'))
def add_employee():
    employee = view.EmployeeView()
    response = employee.create('add_employee.html',
                               redirect='employees')
    if employee.form.validate_on_submit():
        document.EmployeeDoc.create(employee=employee)
    return response


@view.EmployeeView.edit_page
@app.route('/employee/edit/<id>', methods=('POST', 'GET'))
def edit_employee(id):
    return view.EmployeeView(id).edit('edit_employee.html',
                                      redirect='employees')


@view.EmployeeView.view_page
@app.route('/employee/view/<id>')
def view_employee(id):
    history = document.EmployeeDoc(id).history
    return view.EmployeeView(id).view('view_employee.html', history=history)


@view.EmployeeView.delete_page
@app.route('/employee/delete/<id>', methods=('POST', 'GET'))
def delete_employee(id):
    return view.EmployeeView(id).delete('delete_employee.html',
                                        redirect='employees')


@app.route('/employee/edit_template/<id>', methods=('POST', 'GET'))
@app.route('/employee/edit_template/<id>/<version>', methods=('POST', 'GET'))
def edit_employee_report(id, version=None):
    employee = view.EmployeeView(id)
    doc = document.EmployeeDoc
    return doc.edit('edit_employee_template.html',
                    employee=employee,
                    version=version)


@app.route('/employee/html/<id>')
@app.route('/employee/html/<id>/<version>')
def html_employee(id, version=None):
    doc = document.EmployeeDoc
    return doc.html('employee_report.html',
                    employee=view.EmployeeView(id),
                    version=version)


@app.route('/employee/download/<id>')
@app.route('/employee/download/<id>/<version>')
def pdf_employee(id, version=None):
    doc = document.EmployeeDoc
    return doc.download_pdf(filename='Employee %s report' % (id),
                            employee=view.EmployeeView(id),
                            version=version)


if __name__ == '__main__':
    app.db.create_all()
    app.secret_key = 'Azerty'
    app.run(debug=True, host='127.0.0.1', port=8000)
