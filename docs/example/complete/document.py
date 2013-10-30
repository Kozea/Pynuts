from .application import nuts


class EmployeeDoc(nuts.Document):

    model_path = 'models/'
    document_id_template = '{employee.data.person_id}'

    def render_employee(self, data):
        """Render the employee table."""
        return self.jinja_environment.get_template(
            'employee.jinja2').render(data=data)
