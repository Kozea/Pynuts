from application import app


class EmployeeDoc(app.Document):

    model = 'models/'
    document_id_template = '{employee.data.id}'
    repository = '/tmp/employees.git'
