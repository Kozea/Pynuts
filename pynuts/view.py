"""View file for Pynuts."""

import flask
import jinja2
from sqlalchemy.orm import class_mapper
from sqlalchemy.util import classproperty

# Set the jinja2 environment by defining templates location and globals.
JINJA2_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.PackageLoader('pynuts', 'templates'))
JINJA2_ENVIRONMENT.globals.update({'url_for': flask.url_for})


class MetaView(type):
    """Metaclass for view classes."""
    def __init__(metacls, name, bases, dict_):
        if metacls.model:
            metacls._mapping = metacls._mapping or class_mapper(metacls.model)
            column_names = (column.key for column in metacls._mapping.columns)
            metacls.view_columns = metacls.view_columns or column_names
            metacls.table_columns = metacls.table_columns or column_names
            metacls.edit_columns = metacls.edit_columns or column_names
            metacls.create_columns = metacls.create_columns or column_names
        super(MetaView, metacls).__init__(name, bases, dict_)


class ModelView(object):
    """Model view class.

    Different attributes are set here :

    'Metaclass' : Define the metaclass

    'Mapper' : The SQLAlchemy class mapper

    'Model' : The SQLAlchemy model view

    'Form' : WTForms form
             MyView(ModelView):
                    class Form(Form):
                        id = IntegerField(u'Id', validators=[Required()])
                        name = TextField(u'Last name', validators=[Required()])

    'Endpoints' : Endpoints for the flask url_for method in templates
                  Add a decorator on your routes to automatically set
                  the endpoint (see below)

    'Templates' : Pynuts templates name

    'Columns' : Model columns displayed in CRUD routes
                MyView(ModelView):
                      create_columns : ('name','address')

    """

    # Metaclass
    __metaclass__ = MetaView

    # Mapper
    _mapping = None

    # SQLAlchemy model
    model = None

    # WTForms view form
    form = None

    # Endpoints
    add_endpoint = None
    edit_endpoint = None
    delete_endpoint = None
    view_endpoint = None

    # Templates
    view_template = 'view.jinja2'
    list_template = 'list.jinja2'
    table_template = 'table.jinja2'
    edit_template = 'edit.jinja2'
    create_template = 'create.jinja2'

    # Columns
    list_column = None
    view_columns = None
    table_columns = None
    edit_columns = None
    create_columns = None

    # Methods
    def __init__(self, keys=None, element=None):
        if keys:
            self.data = self.model.query.get_or_404(keys)
        elif element:
            self.data = element
        self.form = self.Form(flask.request.form, obj=self.data)

    @classmethod
    def all(cls):
        """Return all the elements of the SQLAlchemy class."""
        for element in cls.model.query.all():
            yield cls(element=element)

    @classproperty
    def session(cls):
        """Set the database session."""
        return cls.model.query.session

    @staticmethod
    def _get_form_attributes(form):
        """Return the form attributes."""
        return {
            key: form[key].data for key in flask.request.form}

    def template_url_for(self, endpoint):
        """Return endpoint if callable, url_for this endpoint else."""
        if callable(endpoint):
            return endpoint(self, **self.primary_keys)
        else:
            return flask.url_for(endpoint)

    def action_url_for(self, action):
        """Return url_for."""
        return self.template_url_for(
            getattr(type(self), '%s_endpoint' % action))

    # Endpoints methods
    @classmethod
    def edit_page(cls, function):
        """Set the endpoint according to the function name."""
        cls.edit_endpoint = \
            lambda cls, **primary_keys: flask.url_for(
                function.__name__, **primary_keys)
        return function

    @classmethod
    def add_page(cls, function):
        """Set the endpoint according to the function name."""
        cls.add_endpoint = function.__name__
        return function

    @classmethod
    def delete_page(cls, function):
        """Set the endpoint according to the function name."""
        cls.delete_endpoint = \
            lambda cls, **primary_keys: flask.url_for(
                function.__name__, **primary_keys)
        return function

    @classmethod
    def view_page(cls, function):
        """Set the endpoint according to the function name."""
        cls.view_endpoint = \
            lambda cls, **primary_keys: flask.url_for(
                function.__name__, **primary_keys)
        return function

    # View methods
    @classmethod
    def view_list(cls):
        """Render the HTML for list_template."""
        template = JINJA2_ENVIRONMENT.get_template(cls.list_template)
        return jinja2.Markup(template.render(cls=cls))

    def view_object(self):
        """Render the HTML for view_template."""
        template = JINJA2_ENVIRONMENT.get_template(self.view_template)
        return jinja2.Markup(template.render(obj=self))

    @classmethod
    def view_table(cls):
        """Render the HTML for table_template."""
        template = JINJA2_ENVIRONMENT.get_template(cls.table_template)
        return jinja2.Markup(template.render(cls=cls))

    @classmethod
    def view_create(cls):
        """Render the HTML for create_template."""
        template = JINJA2_ENVIRONMENT.get_template(cls.create_template)
        return jinja2.Markup(template.render(cls=cls))

    def view_edit(self):
        """Render the HTML for edit_template."""
        template = JINJA2_ENVIRONMENT.get_template(self.edit_template)
        return jinja2.Markup(template.render(obj=self))

    # CRUD methods
    @classmethod
    def list(cls, template=None, *args, **kwargs):
        """Return the list_template."""
        return flask.render_template(template, cls=cls, *args, **kwargs)

    @classmethod
    def table(cls, template=None, *args, **kwargs):
        """Return the table_template."""
        return flask.render_template(template, cls=cls, *args, **kwargs)

    @classmethod
    def create(cls, template=None, redirect=None, values=None,
               *args, **kwargs):
        """Define the create method.

        Also check the values in the form.

        If the values are OK : commit the form with its data.

        Else : Display the form with errors.

        """
        form = cls.Form(flask.request.form)
        if form.validate_on_submit():
            form_values = cls._get_form_attributes(form)
            if values:
                form_values.update(values)
            obj = cls(element=cls.model(**form_values))
            cls.session.add(obj.data)
            cls.session.commit()
            return flask.redirect(obj.template_url_for(redirect))
        return flask.render_template(template, cls=cls, *args, **kwargs)

    def edit(self, template=None, redirect=None, *args, **kwargs):
        """Return the edit_template.

        Also check the values in the form.

        If the values are OK : commit the form with its data.

        Else : Display the form with errors.

        """
        if self.form.validate_on_submit():
            for key, value in self._get_form_attributes(self.form).items():
                setattr(self.data, key, value)
            self.session.commit()
            return flask.redirect(self.template_url_for(redirect))
        return flask.render_template(template, obj=self, *args, **kwargs)

    def delete(self, redirect=None):
        """Delete an entry from the database."""
        self.session.delete(self.data)
        self.session.commit()
        return flask.redirect(flask.url_for(redirect))

    def view(self, template=None, *args, **kwargs):
        """Return the view_template."""
        self.form.process(obj=self.data)
        return flask.render_template(
            template, obj=self, *args, **kwargs)

    # Misc methods
    @property
    def primary_keys(self):
        """Return a primary_keys/value dict."""
        return {
            column.key: getattr(self.data, column.key)
            for column in self._mapping.primary_key}
