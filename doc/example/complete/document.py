from application import app


class EmployeeDoc(app.Document):

    model_path = 'models/'
    document_id_template = '{employee.data.person_id}'
