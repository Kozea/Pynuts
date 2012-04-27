from application import app


class EmployeeDoc(app.Document):

    settings = {'initial_header_level': 3,
                'embed_stylesheet': False,
                'stylesheet_path': None}

    model = 'models/report'
    document_id_template = '{employee.data.id}'
    repository = '/tmp/employees.git'
