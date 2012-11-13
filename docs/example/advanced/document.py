from application import nuts


class EmployeeDoc(nuts.Document):

    model_path = 'models/'
    document_id_template = '{employee.data.person_id}'
