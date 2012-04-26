Quickstart
==========

A Minimal application
---------------------



A minimal Pynuts application looks something like this:

A basic Pynuts application required 4 parts:

- An executable
- An application file which provides a Flask application
- A view class extended from pynuts ModelView
- A SQLAlchemy class 
    
``executable.py``::

    import flask
    
    from .application import app

    @app.route('/')
    @app.route('/employees/')
    def employees():
        return view.EmployeeView.list('list_employees.html')

    if __name__ == '__main__':
        app.db.create_all()
        app.secret_key = 'Azerty'
        app.run(debug=True, host='127.0.0.1', port=5000)

``application.py``::

    import pynuts

    CONFIG = {
        'CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'}


    app = pynuts.Pynuts(__name__, config=CONFIG)

``view.py``:: 
    
    from pynuts.field import EditableField
    from flask.ext.wtf import Form, TextField, IntegerField, Required

    from . import database
    from .application import app

    class EmployeeView(app.ModelView):
        model = database.Employee

        view_columns = ('id', 'name')
    
        class Form(Form):
            id = IntegerField(u'ID', validators=[Required()])
            name = TextField(u'Surname', validators=[Required()])

``database.py``::

    from .application import app
    
    
    class Employee(app.db.Model):
        __tablename__ = 'Employee'
        id = app.db.Column(app.db.Integer(), primary_key=True)
        name = app.db.Column(app.db.String())


Then run the server ::

    $ python executable.py
    * Running on http://127.0.0.1:5000/

Now head over to http://127.0.0.1:5000/, and you should see your list of employees.

So what did that code do?

    First we imported the Flask class. An instance of this class will be our WSGI application. The first argument is the name of the application’s module. If you are using a single module (as in this example), you should use __name__ because depending on if it’s started as application or imported as module the name will be different ('__main__' versus the actual import name). For more information, have a look at the Flask documentation.
    Next we create an instance of this class. We pass it the name of the module or package. This is needed so that Flask knows where to look for templates, static files, and so on.
    We then use the route() decorator to tell Flask what URL should trigger our function.
    The function is given a name which is also used to generate URLs for that particular function, and returns the message we want to display in the user’s browser.
    Finally we use the run() function to run the local server with our application. The if __name__ == '__main__': makes sure the server only runs if the script is executed directly from the Python interpreter and not used as imported module.

To stop the server, hit control-C.
