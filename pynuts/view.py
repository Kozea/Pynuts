"""View file for Pynuts."""

import flask
import jinja2
from sqlalchemy.orm import class_mapper
from sqlalchemy.util import classproperty

from .environment import create_environment


class MetaView(type):
    """Metaclass for view classes."""
    def __init__(cls, name, bases, dict_):
        if cls.model:
            cls._mapping = cls._mapping or class_mapper(cls.model)
            column_names = (column.key for column in cls._mapping.columns)
            cls.view_columns = cls.view_columns or column_names
            cls.table_columns = cls.table_columns or column_names
            cls.edit_columns = cls.edit_columns or column_names
            cls.create_columns = cls.create_columns or column_names
        super(MetaView, cls).__init__(name, bases, dict_)


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

    # Jinja2 environment
    environment = create_environment()

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
    delete_template = 'delete.jinja2'

    # Columns
    list_column = None
    view_columns = None
    table_columns = None
    edit_columns = None
    create_columns = None

    # Methods
    def __init__(self, keys=None, data=None):
        if keys:
            self.data = self.model.query.get_or_404(keys)
        elif data:
            self.data = data
        else:
            self.data = None
        self.form = self.Form(flask.request.form, obj=self.data)

    @classmethod
    def query(cls, query=None):
        """Return all the elements of the SQLAlchemy class."""
        for data in (query or cls.model.query).all():
            yield cls(data=data)

    @classproperty
    def mapping(cls):
        """Table mapping."""
        return cls._mapping

    @classproperty
    def session(cls):
        """Database session."""
        return cls.model.query.session

    @staticmethod
    def _get_form_attributes(form):
        """Return the form attributes."""
        return {
            key: form[key].data for key in flask.request.form}

    def handle_errors(self):
        if self.form.errors:
            for key, errors in self.form.errors.items():
                flask.flash(jinja2.Markup(
                    u'<label for="%s">%s</label>: %s.' % (
                        key, self.form[key].label.text, ', '.join(errors))),
                'error')

    def template_url_for(self, endpoint):
        """Return endpoint if callable, url_for this endpoint else."""
        if callable(endpoint):
            return endpoint(self, **self.primary_keys)
        else:
            return endpoint

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
    def view_list(cls, query=None, endpoint=None):
        """Render the HTML for list_template."""
        template = cls.environment.get_template(cls.list_template)
        return jinja2.Markup(template.render(
            cls=cls, query=query, endpoint=endpoint))

    def view_object(self):
        """Render the HTML for view_template."""
        template = self.environment.get_template(self.view_template)
        return jinja2.Markup(template.render(obj=self))

    @classmethod
    def view_table(cls, query=None, endpoint=None):
        """Render the HTML for table_template."""
        template = cls.environment.get_template(cls.table_template)
        return jinja2.Markup(template.render(
            cls=cls, query=query, endpoint=endpoint))

    def view_create(self):
        """Render the HTML for create_template."""
        template = self.environment.get_template(self.create_template)
        return jinja2.Markup(template.render(obj=self))

    def view_edit(self):
        """Render the HTML for edit_template."""
        template = self.environment.get_template(self.edit_template)
        return jinja2.Markup(template.render(obj=self))

    def view_delete(self):
        """Render the HTML for edit_template."""
        template = self.environment.get_template(self.delete_template)
        return jinja2.Markup(template.render(obj=self))

    # CRUD methods
    @classmethod
    def list(cls, template=None, query=None, **kwargs):
        """Return the list_template."""
        return flask.render_template(template, cls=cls, query=query, **kwargs)

    @classmethod
    def table(cls, template=None, query=None, **kwargs):
        """Return the table_template."""
        return flask.render_template(template, cls=cls, query=query, **kwargs)

    def create(self, template=None, redirect=None, values=None, **kwargs):
        """Define the create method.

        Also check the values in the form.

        If the values are OK : commit the form with its data.

        Else : Display the form with errors.

        """
        if self.form.validate_on_submit():
            form_values = self._get_form_attributes(self.form)
            if values:
                form_values.update(values)
            self.data = self.model(**form_values)
            self.session.add(self.data)
            self.session.commit()
            return flask.redirect(self.template_url_for(redirect))
        self.handle_errors()
        return flask.render_template(template, obj=self, **kwargs)

    def edit(self, template=None, redirect=None, **kwargs):
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
        self.handle_errors()
        return flask.render_template(template, obj=self, **kwargs)

    def delete(self, template=None, redirect=None, **kwargs):
        """Delete an entry from the database."""
        if flask.request.method == 'POST':
            self.session.delete(self.data)
            self.session.commit()
            return flask.redirect(flask.url_for(redirect))
        return flask.render_template(template, obj=self, **kwargs)

    def view(self, template=None, **kwargs):
        """Return the view_template."""
        self.form.process(obj=self.data)
        return flask.render_template(template, obj=self, **kwargs)

    # Misc methods
    @property
    def primary_keys(self):
        """Primary_keys/value dict."""
        return {
            column.key: getattr(self.data, column.key)
            for column in self.mapping.primary_key}

    @property
    def name(self):
        """Common name."""
        return getattr(self.data, self.list_column)
