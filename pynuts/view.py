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
    """This class represents the view of a SQLAlchemy model class.

    It grants CRUD operations and offers the view corresponding.

    :param keys: Your model primary keys
    :type keys: String, Tuple

    :param data: Your model data
    :type data: Dict

    """

    # Metaclass
    __metaclass__ = MetaView

    # Mapper
    _mapping = None

    # Jinja2 environment
    environment = create_environment()

    #: SQLAlchemy model
    model = None

    form = None
    """
    WTForms view form. Declare it in your view like this:

    >>> MyView(ModelView):
    ...     class Form(Form):
    ...         id = IntegerField(u'Id', validators=[Required()])
    ...         name = TextField(u'Last name', validators=[Required()])
    """

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

    #: The column which represents your class
    list_column = None

    #: The columns displayed in the view list
    view_columns = None

    #: The columns displayed in the table
    table_columns = None

    #: The columns you can edit
    edit_columns = None

    #: The column you can set when creating an instance
    create_columns = None

    # Properties
    @property
    def primary_keys(self):
        """Primary keys/value dict."""
        return {
            column.key: getattr(self.data, column.key)
            for column in self.mapping.primary_key}

    @property
    def name(self):
        """Common name."""
        return getattr(self.data, self.list_column)

    # Methods
    def __init__(self, keys=None, data=None):
        if keys:
            self.data = self.model.query.get_or_404(keys)
        elif data:
            self.data = data
        else:
            self.data = None
        self.form = self.Form(flask.request.form, obj=self.data)

    @classproperty
    def mapping(cls):
        """Table mapping."""
        return cls._mapping

    @classproperty
    def session(cls):
        """Database session."""
        return cls.model.query.session

    @classmethod
    def query(cls, query=None):
        """Return all the model elements according to a query..

        :param query: The SQLAlchemy query
        :type query: String

        """
        for data in (query or cls.model.query).all():
            yield cls(data=data)

    @staticmethod
    def _get_form_attributes(form):
        """Return the form attributes."""
        return {
            key: form[key].data for key in flask.request.form}

    def handle_errors(self):
        """Flash all the errors contained in the form."""
        if self.form.errors:
            for key, errors in self.form.errors.items():
                flask.flash(jinja2.Markup(
                    u'<label for="%s">%s</label>: %s.' % (
                        key, self.form[key].label.text, ', '.join(errors))),
                'error')

    def template_url_for(self, endpoint):
        """Return endpoint if callable, url_for this endpoint else.

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: String, func(lambda)

        """
        if callable(endpoint):
            return endpoint(self, **self.primary_keys)
        else:
            return endpoint

    def action_url_for(self, action):
        """Return url_for for CRUD operation.

        :param action: Endpoint name
        :type action: String

        """
        return self.template_url_for(
            getattr(type(self), '%s_endpoint' % action))

    # Endpoints methods
    @classmethod
    def edit_page(cls, function):
        """Set the edit_endpoint according to the function name."""
        cls.edit_endpoint = \
            lambda cls, **primary_keys: flask.url_for(
                function.__name__, **primary_keys)
        return function

    @classmethod
    def add_page(cls, function):
        """Set the add_endpoint according to the function name."""
        cls.add_endpoint = function.__name__
        return function

    @classmethod
    def delete_page(cls, function):
        """Set the delete_endpoint according to the function name."""
        cls.delete_endpoint = \
            lambda cls, **primary_keys: flask.url_for(
                function.__name__, **primary_keys)
        return function

    @classmethod
    def view_page(cls, function):
        """Set the view_endpoint according to the function name."""
        cls.view_endpoint = \
            lambda cls, **primary_keys: flask.url_for(
                function.__name__, **primary_keys)
        return function

    # View methods
    @classmethod
    def view_list(cls, query=None, endpoint=None):
<<<<<<< HEAD
        """Render the HTML for list_template.

        :param query: The SQLAlchemy query
        :type query: String

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: String, func(lambda)

        """
        template = JINJA2_ENVIRONMENT.get_template(cls.list_template)
        return jinja2.Markup(template.render(
            cls=cls, query=query, endpoint=endpoint))

    @classmethod
    def view_table(cls, query=None, endpoint=None):
        """Render the HTML for table_template.

        :param query: The SQLAlchemy query
        :type query: String

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: String, func(lambda)

        """
        template = JINJA2_ENVIRONMENT.get_template(cls.table_template)
=======
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

    def view_object(self):
        """Render the HTML for view_template."""
        template = JINJA2_ENVIRONMENT.get_template(self.view_template)
        return jinja2.Markup(template.render(obj=self))

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
        """Return the list_template.

        :param template: The template you want to render
        :type template: String

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: String, func(lambda)

        """
        return flask.render_template(template, cls=cls, query=query, **kwargs)

    @classmethod
    def table(cls, template=None, query=None, **kwargs):
        """Return the table_template.

        :param template: The template you want to render
        :type template: String

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: String, func(lambda)

        """
        return flask.render_template(template, cls=cls, query=query, **kwargs)

    def create(self, template=None, redirect=None, values=None, **kwargs):
        """Define the create method. Also check the values in the form: \

        If the values are OK : commit the form with its data; \

        Else : Display the form with errors.

        :param template: The template you want to render
        :type template: String

        :param redirect: The URL where you want to redirect after the function
        :type redirect: String

        :param values: The values of the object you want to create
        :type values: Dict

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
        """Return the edit_template. See the create method for more details.

        :param template: The template you want to render
        :type template: String

        :param redirect: The URL where you want to redirect after the function
        :type redirect: String

        """
        if self.form.validate_on_submit():
            for key, value in self._get_form_attributes(self.form).items():
                setattr(self.data, key, value)
            self.session.commit()
            return flask.redirect(self.template_url_for(redirect))
        self.handle_errors()
        return flask.render_template(template, obj=self, **kwargs)

    def delete(self, template=None, redirect=None, **kwargs):
        """Delete an entry from the database.

        :param template: The template you want to render
        :type template: String

        :param redirect: The URL where you want to redirect after the function
        :type redirect: String

        """
        if flask.request.method == 'POST':
            self.session.delete(self.data)
            self.session.commit()
            return flask.redirect(flask.url_for(redirect))
        return flask.render_template(template, obj=self, **kwargs)

    def view(self, template=None, **kwargs):
        """Return the view_template.

        :param template: The template you want to render
        :type template: String

        """
        self.form.process(obj=self.data)
        return flask.render_template(template, obj=self, **kwargs)
