from flask import flash, redirect, session, request, render_template, url_for

from application import app
from pynuts.rights import allow_if
import view
import document
import rights as Is


@app.errorhandler(403)
@app.route('/login')
def login(error=None):
    return render_template('login.html')


@app.route('/login', methods=('POST', ))
def login_post():
    login = request.form.get('login')
    password = request.form.get('password')
    employee = view.EmployeeView.model.query.filter_by(
        login=login, password=password).first()
    if employee:
        session['id'] = employee.person_id
        session['login'] = login
        flash('You were logged in !', 'ok')
    else:
        flash('invalid credentials', 'error')
    return redirect('employees')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('employees')


@app.route('/')
@app.route('/employees/')
@allow_if(Is.connected)
def employees():
    return view.EmployeeView.list('list_employees.html')


@app.route('/employees/table')
@allow_if(Is.connected)
def table_employees():
    return view.EmployeeView.table('table_employees.html')


@app.route('/employee/create/', methods=('POST', 'GET'))
@allow_if(Is.admin)
def create_employee():
    employee = view.EmployeeView()
    response = employee.create('create_employee.html',
                               redirect='employees')
    if employee.create_form.validate_on_submit():
        document.EmployeeDoc.create(employee=employee)
    return response


@view.EmployeeView.read_page
@app.route('/employee/read/<int:person_id>')
@allow_if(Is.admin | Is.connected_user)
def read_employee(person_id=None):
    history = document.EmployeeDoc(person_id).history
    return view.EmployeeView(person_id).read(
        'read_employee.html', history=history)


@view.EmployeeView.update_page
@app.route('/employee/update/', methods=('POST', 'GET'))
@app.route('/employee/update/<int:person_id>', methods=('POST', 'GET'))
@allow_if(Is.admin | Is.connected_user)
def update_employee(person_id=None):
    return view.EmployeeView(person_id or app.context.person).update(
        'update_employee.html', redirect='employees')


@view.EmployeeView.delete_page
@app.route('/employee/delete/<int:person_id>', methods=('POST', 'GET'))
@allow_if(Is.admin)
def delete_employee(person_id):
    return view.EmployeeView(person_id).delete('delete_employee.html',
                                        redirect='employees')


@app.route('/employee/edit_template/<int:person_id>', methods=('POST', 'GET'))
@app.route('/employee/edit_template/<int:person_id>/<version>',
           methods=('POST', 'GET'))
@allow_if(Is.admin | Is.connected_user)
def edit_employee_report(person_id, version=None):
    employee = view.EmployeeView(person_id)
    doc = document.EmployeeDoc
    return doc.edit('edit_employee_template.html',
                    employee=employee,
                    version=version)


@app.route('/employee/html/<int:person_id>')
@app.route('/employee/html/<int:person_id>/<version>')
@allow_if(Is.admin | Is.connected_user)
def html_employee(person_id, version=None):
    doc = document.EmployeeDoc
    return doc.html('employee_report.html',
                    employee=view.EmployeeView(person_id),
                    version=version)


@app.route('/employee/download/<int:person_id>')
@app.route('/employee/download/<int:person_id>/<version>')
@allow_if(Is.admin | Is.connected_user)
def pdf_employee(person_id, version=None):
    doc = document.EmployeeDoc
    return doc.download_pdf(
        filename='Employee %s report' % (person_id),
        employee=view.EmployeeView(person_id), version=version)


if __name__ == '__main__':
    app.db.create_all()
    app.secret_key = 'Azerty'
    app.run(debug=True, host='127.0.0.1', port=8000)
