# *-* coding: utf-8 *-*
from datetime import datetime
from flask import (
    flash, redirect, session, request, render_template, url_for, g)

from application import app
from pynuts.rights import allow_if
from pynuts.directives import Editable
from pynuts.document import Content
import view
import document
from database import Employee, Company
import rights as Is
from exception import NoPermission


@app.errorhandler(403)
def login(error):
    """Forbidden error handler."""
    return render_template('login.html'), 403


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


@app.route('/test_rights')
@allow_if((Is.connected & ~ Is.admin) | (Is.dummy & Is.admin) | (
    Is.dummy | Is.admin) | (Is.dummy ^ Is.admin) | (Is.connected ^ Is.admin),
          NoPermission)
def test_rights():
    """Test rights route."""
    return redirect(url_for('employees'))


@app.route('/logout')
@allow_if(Is.connected)
def logout():
    """Logout route."""
    session.clear()
    return render_template('login.html')


@view.EmployeeView.list_page
@app.route('/')
@app.route('/employees/')
@allow_if(Is.connected)
def employees():
    return view.EmployeeView.list('list_employees.html')


@app.route('/companies/')
@allow_if(Is.connected)
def companies():
    return view.CompanyView.list('list_companies.html')


@view.EmployeeView.table_page
@app.route('/employees/table')
@allow_if(Is.connected)
def table_employees():
    return view.EmployeeView.table(
        'table_employees.html')


@view.EmployeeView.create_page
@app.route('/employee/create/', methods=('POST', 'GET'))
@allow_if(Is.admin)
def create_employee():
    employee = view.EmployeeView()
    response = employee.create('create_employee.html',
                               action=url_for('create_employee'),
                               values={'company_id': '9999'},
                               redirect='employees')
    if employee.create_form.validate_on_submit():
        document.EmployeeDoc.create(employee=employee)
        employee.data.set_order_to_last(Employee.company_id == employee.data.co)
        app.db.session.commit()
    return response


@view.CompanyView.create_page
@app.route('/company/create/', methods=('POST', 'GET'))
@allow_if(Is.admin)
def create_company():
    company = view.CompanyView()
    response = company.create('create_company.html', redirect='companies')
    return response


@view.EmployeeView.read_page
@app.route('/employee/read/<int:person_id>')
@allow_if(Is.admin | Is.connected_user)
def read_employee(person_id=None):
    doc = document.EmployeeDoc(person_id)
    content = Content(doc.git, 'logo.png')
    return view.EmployeeView(person_id).read(
        'read_employee.html', doc=doc, content=content)


@app.route('/company/read/<int:company_id>/'
           'employee/table/<int:person_id>/up')
@allow_if(Is.connected)
def up_employee(company_id, person_id):
    Employee.query.get(person_id).up(Employee.company_id == company_id)
    Employee.query.session.commit()
    return redirect(url_for('read_company', company_id=company_id))


@app.route('/company/read/<int:company_id>/'
           'employee/table/<int:person_id>/down')
@allow_if(Is.connected)
def down_employee(company_id, person_id):
    Employee.query.get(person_id).down(Employee.company_id == company_id)
    Employee.query.session.commit()
    return redirect(url_for('read_company', company_id=company_id))


@view.CompanyView.read_page
@app.route('/company/read/<int:company_id>')
@allow_if(Is.admin)
def read_company(company_id=None):
    company_view = view.CompanyView(company_id)
    employee_table = view.EmployeeView.view_table(
        actions=[{
            'label': u'٧',
            'title': u'Down',
            'endpoint': 'down_employee',
            'data': {
                'company_id': company_id
            }
        }, {
            'label': u'٨',
            'title': u'Up',
            'endpoint': 'up_employee',
            'data': {
                'company_id': company_id
            }
        }],
        elements=company_view.data.employees)
    return company_view.read('read_company.html', table=employee_table)


@view.EmployeeView.update_page
@app.route('/employee/update/', methods=('POST', 'GET'))
@app.route('/employee/update/<int:person_id>', methods=('POST', 'GET'))
@allow_if(Is.admin | Is.connected_user)
def update_employee(person_id=None):
    return view.EmployeeView(person_id or g.context.person).update(
        'update_employee.html', action="lol", redirect='employees')


@view.EmployeeView.delete_page
@app.route('/employee/delete/<int:person_id>', methods=('POST', 'GET'))
@allow_if(Is.admin)
def delete_employee(person_id):
    employee_view = view.EmployeeView(person_id)
    if request.method == 'POST':
        employee_view.data.reorder(
            Employee.company_id == employee_view.data.company_id)
    return employee_view.delete(
        'delete_employee.html', redirect='employees')


@app.route('/employee/edit_template/<int:person_id>', methods=('POST', 'GET'))
@app.route('/employee/edit_template/<int:person_id>/<version>',
           methods=('POST', 'GET'))
@allow_if(Is.admin | Is.connected_user)
def edit_employee_report(person_id, version=None):
    employee = view.EmployeeView(person_id)
    doc = document.EmployeeDoc
    return doc.edit('edit_employee_template.html',
                    employee=employee,
                    version=version,
                    redirect_url='employees')


@app.route('/employee/archive_template/<int:person_id>', methods=('POST',))
@app.route('/employee/archive_template/<int:person_id>/<version>',
           methods=('POST',))
@allow_if(Is.admin | Is.connected_user)
def archive_employee_report(person_id, version=None):
    employee = view.EmployeeView(person_id)
    doc = document.EmployeeDoc
    doc.archive(employee=employee)
    flash('The report was sucessfully archived.', 'ok')
    return redirect(url_for('read_employee', person_id=person_id))


@app.route('/employee/html/<int:person_id>')
@app.route('/employee/html/<int:person_id>/<version>')
@allow_if(Is.admin | Is.connected_user)
def html_employee(person_id, version=None):
    doc = document.EmployeeDoc
    return doc.html('employee_report.html', archive=False,
                    employee=view.EmployeeView(person_id),
                    version=version)


@app.route('/employee/html/<int:person_id>/archive')
@app.route('/employee/html/<int:person_id>/<version>/archive')
@allow_if(Is.admin | Is.connected_user)
def archived_html_employee(person_id, version=None):
    doc = document.EmployeeDoc
    return doc.html('employee_report.html', archive=True,
                    employee=view.EmployeeView(person_id),
                    version=version)


@app.route('/employee/download/<int:person_id>')
@app.route('/employee/download/<int:person_id>/<version>')
@allow_if(Is.admin | Is.connected_user)
def pdf_employee(person_id, version=None):
    doc = document.EmployeeDoc
    return doc.download_pdf(
        filename='Employee %s report' % (person_id), archive=False,
        employee=view.EmployeeView(person_id), version=version)


@app.route('/employee/download/<int:person_id>/archive')
@app.route('/employee/download/<int:person_id>/<version>/archive')
@allow_if(Is.admin | Is.connected_user)
def archived_pdf_employee(person_id, version=None):
    doc = document.EmployeeDoc
    return doc.download_pdf(
        filename='Employee %s report' % (person_id), archive=True,
        employee=view.EmployeeView(person_id), version=version)


@app.route('/test_endpoint/<int:company_id>')
def test_endpoint(company_id):
    return redirect(url_for('read_company', company_id=company_id))


@app.route('/edit_image_post/<int:person_id>', methods=('POST', 'GET'))
def edit_image(person_id):
    if request.method == 'GET':
        return render_template('edit_image.html')
    else:
        content = document.EmployeeDoc(person_id).get_content('logo.png')
        content.write(request.files['image'].read())
        return redirect(url_for('read_employee', person_id=person_id))


@app.before_request
def set_request_time():
    g.context.request_time = datetime.now().strftime('%Y/%m/%d')


if __name__ == '__main__':  # pragma: no cover
    app.db.create_all()
    app.secret_key = 'Azerty'
    app.run(debug=True, host='127.0.0.1', port=8000)
