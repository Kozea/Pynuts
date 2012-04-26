from application import app
import view


@app.route('/')
@app.route('/employees/')
def employees():
    return view.EmployeeView.list('list_employees.html')


@app.route('/employee/add/', methods=('POST', 'GET'))
def add_employee():
    return view.EmployeeView().create('add_employee.html',
                                      redirect='employees')


if __name__ == '__main__':
    app.db.create_all()
    app.secret_key = 'Azerty'
    app.run(debug=True, host='127.0.0.1', port=5000)
