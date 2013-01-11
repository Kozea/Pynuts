"""View file for Pynuts."""

import flask
import jinja2
from flask_wtf import Form, TextField
from functools import wraps
from werkzeug.utils import cached_property
from werkzeug.datastructures import FileStorage
from sqlalchemy.orm import class_mapper
from sqlalchemy.util import classproperty
from sqlalchemy.orm.attributes import InstrumentedAttribute

ACTIONS = ('list', 'table', 'create', 'read', 'update', 'delete')


def auth_url_for(endpoint, **kwargs):
    ep_fun = flask.current_app.view_functions.get(endpoint)
    if ep_fun and hasattr(ep_fun, '_auth_fun'):
        if ep_fun._auth_fun(**kwargs):
            return flask.url_for(endpoint, **kwargs)
        return
    return flask.url_for(endpoint, **kwargs)


class PynutsMROException(Exception):
    pass


class BaseForm(Form):

    def handle_errors(self):
        """Flash all the form errors."""
        if self.errors:
            for key, errors in self.errors.items():
                flask.flash(jinja2.Markup(
                    u'<label for="%s">%s</label>: %s.' % (
                        key, self[key].label.text, ', '.join(errors))),
                    'error')


class MetaView(type):
    """Metaclass for view classes."""
    def __init__(cls, name, bases, dict_):
        super(MetaView, cls).__init__(name, bases, dict_)
        # For middle class
        if not cls.Form:
            return

        # TODO: find a better name than the name of the class
        cls._pynuts.views[cls.__name__] = cls

        cls.list_columns = cls.list_column and (cls.list_column,)

        for action in ACTIONS:
            # Make action_page
            def make_action_page(action):
                def action_page(cls, function):
                    """ Set the action_endpoint class property according
                    to the function name.
                    """
                    check_auth = getattr(function, '_auth_fun',
                                         lambda **kwargs: True)
                    setattr(cls, '%s_auth' % action, staticmethod(check_auth))
                    setattr(cls, '%s_endpoint' % action, function.__name__)

                    return function

                action_page.__name__ = '%s_page' % action
                return action_page
            setattr(cls, '%s_page' % action,
                    classmethod(make_action_page(action)))

            columns = getattr(cls, '%s_columns' % action, None)
            if not columns:
                continue

            # Make actionForm
            class_name = '%sForm' % action.capitalize()
            classes = [BaseForm]
            form_class = cls.Form
            if form_class and BaseForm not in form_class.__bases__:
                bases = list(form_class.__bases__)
                bases.extend(classes)
                classes = bases

            fields = dict(
                (field_name, getattr(
                    cls.Form, field_name,
                    TextField(field_name)))
                for field_name in columns)
            try:
                form = type(class_name, tuple(classes), fields)
            except TypeError as e:
                raise PynutsMROException(
                    'The form must inherit from the '
                    'pynuts.view.BaseForm class. (%r)' % e)
            setattr(cls, class_name, form)


class ModelView(object):
    """This class represents the view of a SQLAlchemy model class.

    It grants CRUD (Create, Read, Update, Delete) operations
    and provides a specific view for each of these operations.

    :param keys: Your model primary key(s)
    :type keys: str, tuple

    :param data: Your model data
    :type data: dict

    """

    # Metaclass
    __metaclass__ = MetaView

    # Mapper
    _mapping = None

    #: SQLAlchemy model
    model = None

    Form = None
    """
    WTForms view form. Declare it in your view like this:

    >>> class MyView(ModelView):
    ...     class Form(Form):
    ...         id = IntegerField(u'Id', validators=[Required()])
    ...         name = TextField(u'Last name', validators=[Required()])
    """

    # Endpoints
    create_endpoint = None
    read_endpoint = None
    update_endpoint = None
    delete_endpoint = None
    list_endpoint = None
    table_endpoint = None

    # Templates
    view_list_template = '_pynuts/list.jinja2'
    view_table_template = '_pynuts/table.jinja2'
    view_create_template = '_pynuts/create.jinja2'
    view_read_template = '_pynuts/read.jinja2'
    view_update_template = '_pynuts/update.jinja2'
    view_delete_template = '_pynuts/delete.jinja2'

    list_template = None
    table_template = None
    create_template = None
    read_template = None
    update_template = None
    delete_template = None

    #: The column which represents your class
    list_column = None

    #: The columns displayed in the table
    table_columns = None

    #: The column you can set when creating an instance
    create_columns = None

    #: The columns displayed in the view list
    read_columns = None

    #: The columns you can edit
    update_columns = None

    _cached_create_form = None

    def __init__(self, keys=None, data=None):
        if keys is not None:
            self.data = self.model.query.get_or_404(keys)
        else:
            self.data = data

        self.action_url_for = self._action_url_for

    def _action_url_for(self, action, **kwargs):
        kwargs.update(dict(self.primary_keys))
        return type(self).action_url_for(action, **kwargs)

    # Properties
    @property
    def primary_keys(self):
        """Primary keys/value dict."""
        return dict(
            (column.key, getattr(self.data, column.key))
            for column in self.mapping.primary_key)

    @property
    def name(self):
        """Common name."""
        return getattr(self.data, self.list_column)

    @cached_property
    def create_form(self):
        """Return the create form."""
        return self.CreateForm()

    @cached_property
    def read_form(self):
        """Return the read form."""
        return self.ReadForm(formdata=None, obj=self.data)

    @cached_property
    def update_form(self):
        """Return the update form."""
        return self.UpdateForm(obj=self.data)

    @cached_property
    def table_form(self):
        """Return the table form."""
        return self.TableForm(formdata=None, obj=self.data)

    @cached_property
    def list_form(self):
        """Return the list form."""
        return self.ListForm(formdata=None, obj=self.data)

    @cached_property
    def create_fields(self):
        """Return the create fields."""
        return [
            getattr(self.create_form, field) for field in self.create_columns]

    @cached_property
    def read_fields(self):
        """Return the read fields."""
        return [
            getattr(self.read_form, field) for field in self.read_columns]

    @cached_property
    def update_fields(self):
        """Return the update fields."""
        return [
            getattr(self.update_form, field) for field in self.update_columns]

    @cached_property
    def table_fields(self):
        """Return the table fields."""
        return [
            getattr(self.table_form, field) for field in self.table_columns]

    @cached_property
    def list_fields(self):
        """Return the list fields."""
        return [
            getattr(self.list_form, field) for field in self.list_columns]

    @classproperty
    def mapping(cls):
        """Table mapping."""
        return getattr(cls, '_mapping') or class_mapper(cls.model)

    @classproperty
    def session(cls):
        """Database session."""
        return cls.model.query.session

    @classmethod
    def query(cls, query=None, elements=None):
        """Return all the model elements according to a query..

        :param query: The SQLAlchemy query
        :type query: str
        :param elements: A model list (if present, does not execute query)
        :type elements: list

        """
        if elements is not None:
            iterable = elements
        elif query:
            iterable = query.all()
        else:
            iterable = cls.model.query
            if hasattr(cls, 'order_by') and cls.order_by is not None:
                iterable = iterable.order_by(cls.order_by)
            iterable = iterable.all()

        for data in iterable:
            yield cls(data=data)

    @classmethod
    def _get_form_attributes(cls, form):
        """Return the form attributes which are defined on the model."""
        result = {}
        for key in form:
            model_attr = getattr(cls.model, key.name, None)
            if model_attr is not None:
                if (isinstance(model_attr, InstrumentedAttribute) or
                    isinstance(model_attr, property) and model_attr.fset is not
                        None):
                    result[key.name] = key.data
        return result

    @classmethod
    def handle_errors(cls, form):
        """Flash all the errors contained in the form."""
        # Test for attribute if the form has not "handle_errors" method.
        form.handle_errors()

    @classmethod
    def action_url_for(cls, action, **kwargs):
        """Return url_for for CRUD operation.

        :param action: Endpoint name
        :type action: str

        """
        if action not in ACTIONS:
            return flask.url_for(action, **kwargs)
        ep = getattr(cls, '%s_endpoint' % action, None)
        if ep is not None:
            if getattr(cls, '%s_auth' % action)(**kwargs):
                return flask.url_for(ep, **kwargs)

    @classmethod
    def allow_if(cls, auth_fun, exception=None):

        def wrapper(function):
            old_auth_fun = getattr(function, '_auth_fun', None)

            @wraps(function)
            def check_auth(*args, **kwargs):
                """Function wrapper."""
                first = not (len(args) > 0 and issubclass(args[0], ModelView))

                if auth_fun():
                    if not first:
                        args = args[1:]
                    return function(cls, *args, **kwargs)
                elif first:
                    if exception:
                        raise exception
                    else:
                        flask.abort(403)
                else:
                    return function(*args, **kwargs)
            if old_auth_fun:
                check_auth._auth_fun = old_auth_fun | auth_fun
            else:
                check_auth._auth_fun = auth_fun
            return check_auth

        return wrapper

    @classmethod
    def view_list(cls, query=None, no_result_message=None,
                  elements=None, action=None, ctx_args=None, **kwargs):
        """Render the HTML for list_template.

        :param query: The SQLAlchemy query used for rendering the list
        :type query: str
        :param no_result_message: The message displayed if no result
                                  is returned by the query
        :type no_result_message: str
        :param elements: A model list replacing query
        :type elements: list

        """
        ctx_args = ctx_args or {}

        return jinja2.Markup(flask.render_template(
            cls.environment.get_template(cls.view_list_template),
            views=cls.query(query, elements), action=action, ctx_args=ctx_args,
            view_class=cls, no_result_message=no_result_message, **kwargs))

    @classmethod
    def view_table(
            cls, query=None, no_result_message=None,
            elements=None, actions=None, no_default_actions=False,
            ctx_args=None, **kwargs):
        """Render the HTML for table_template.

        :param query: The SQLAlchemy query used for rendering the table
        :type query: str
        :param no_result_message: The message displayed if not any result
                                  is returned by the query
        :type no_result_message: str
        :param elements: A model list replacing query
        :type elements: list

        """
        table_actions = actions or []
        ctx_args = ctx_args or {}

        def actions(view):
            view_actions = []
            for action in table_actions:
                view_action = dict(action)
                view_action.setdefault('data', {})
                view_action['data'].update(view.primary_keys)
                if ctx_args:
                    view_action['data'].update(ctx_args)
                view_action['url'] = auth_url_for(
                    view_action['endpoint'], **view_action['data'])
                view_actions.append(view_action)
            return view_actions

        return jinja2.Markup(flask.render_template(
            cls.environment.get_template(cls.view_table_template).name,
            views=cls.query(query, elements), ctx_args=ctx_args,
            view_class=cls, no_result_message=no_result_message,
            actions=actions, no_default_actions=no_default_actions,
            **kwargs))

    def view_create(self, action=None, **kwargs):
        """Render the HTML for create_template.

        :param action: the URL for the create form validation.

        """
        return jinja2.Markup(flask.render_template(
            self.environment.get_template(self.view_create_template).name,
            view=self, action=action, **kwargs))

    def view_read(self, **kwargs):
        """Render the HTML for read_template."""
        return jinja2.Markup(flask.render_template(
            self.environment.get_template(self.view_read_template).name,
            view=self, **kwargs))

    def view_update(self, action=None, **kwargs):
        """Render the HTML for update_template.

        :param action: the URL for the update form validation.

        """
        return jinja2.Markup(flask.render_template(
            self.environment.get_template(self.view_update_template).name,
            view=self, **kwargs))

    def view_delete(self, **kwargs):
        """Render the HTML for delete_template."""
        return jinja2.Markup(flask.render_template(
            self.environment.get_template(self.view_delete_template).name,
            view=self, **kwargs))

    # CRUD methods
    @classmethod
    def list(cls, template=None, query=None, **kwargs):
        """Return the list_template.

        :param template: The template you want to render
        :type template: str

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: str, func(lambda)

        """
        return flask.render_template(
            template or cls.list_template,
            view_class=cls, query=query, **kwargs)

    @classmethod
    def table(cls, template=None, query=None, **kwargs):
        """Return the table_template.

        :param template: The template you want to render
        :type template: str

        :param endpoint: The endpoint for the registered URL rule
        :type endpoint: str, func(lambda)

        """
        return flask.render_template(
            template or cls.read_template,
            view_class=cls, query=query, **kwargs)

    def create(self, template=None, redirect=None, values=None, **kwargs):
        """Define the create method. Also check the values in the form.

        If the values are OK: commit the form with its data;
        Else: Display the form with errors.

        :param template: The template you want to render
        :type template: str

        :param redirect: The URL where you want to redirect after the function
        :type redirect: str, func(lambda)

        :param values: The values of the object you want to create
        :type values: dict
        """
        if self.handle_create_form(values):
            self.session.commit()
            if redirect in ACTIONS:
                redirect = self.action_url_for(redirect)
            rv = flask.redirect(
                redirect or self.action_url_for(self.read_endpoint))
            return rv
        return flask.render_template(
            template or self.create_template, view=self, **kwargs)

    def handle_create_form(self, values=None):
        """Handle the create form operation.

        If the field value is a ``FileStorage`` instance
        and has a specified UploadSet, the save operation
        will be performed by this UploadSet.

        If the ``FileStorage`` does not have an associated UploadSet,
        it will look for a save handler method named ``{name}_handler``
        (where ``{name}`` is the field name).

        """
        if not self.create_form.validate_on_submit():
            self.handle_errors(self.create_form)
            return False

        form_values = self._get_form_attributes(self.create_form)
        if values:
            form_values.update(values)
        self.data = self.model(**form_values)

        for key, value in form_values.items():
            if isinstance(value, FileStorage):
                if hasattr(self.create_form._fields[key], 'upload_set'):
                    handler = self.create_form._fields[key].upload_set
                    if not handler:
                        raise RuntimeError('No UploadSet handler could be'
                                           'found for %s' % (key))
                else:
                    handler = getattr(self, key + '_handler', None)
                    if not handler:
                        raise ValueError(
                            'You must define a %s_handler '
                            'property on your view set to an UploadSet' %
                            key)
                if value.filename:
                    setattr(self.data, key, handler.save(value))
                else:
                    setattr(self.data, key, None)

        self.session.add(self.data)
        return True

    def update(self, template=None, redirect=None, **kwargs):
        """Return the update_template. See the create method for more details.

        :param template: The template you want to render
        :type template: str

        :param redirect: The URL where you want to redirect after the function
        :type redirect: str, func(lambda)

        """
        if self.handle_update_form():
            self.session.commit()
            if redirect in ACTIONS:
                redirect = self.action_url_for(redirect)
            return flask.redirect(
                redirect or self.action_url_for(self.read_endpoint))
        return flask.render_template(
            template or self.update_template, view=self, **kwargs)

    def handle_update_form(self):
        """Handle the update form operation.

        If the field value is a ``FileStorage`` instance
        and has a specified UploadSet, the save operation
        will be performed by this UploadSet.

        If the ``FileStorage`` does not have an associated UploadSet,
        it will look for a save handler method named ``{name}_handler``
        (where ``{name}`` is the field name).

        """
        if self.update_form.validate_on_submit():
            for key, value in self._get_form_attributes(
                    self.update_form).items():
                if isinstance(value, FileStorage):
                    if hasattr(self.create_form._fields[key], 'upload_set'):
                        handler = self.create_form._fields[key].upload_set
                        if not handler:
                            raise RuntimeError('No UploadSet handler could be'
                                               'found for %s' % (key))
                    else:
                        handler = getattr(self, key + '_handler', None)
                        if not handler:
                            raise ValueError(
                                'You must define a %s_handler '
                                'property on your view set to an UploadSet' %
                                key)
                    if value.filename:
                        setattr(self.data, key, handler.save(value))

                else:
                    setattr(self.data, key, value)
            return True
        self.handle_errors(self.update_form)
        return False

    def read(self, template=None, **kwargs):
        """Return the view_template.

        :param template: The template you want to render
        :type template: str

        """
        self.read_form.process(obj=self.data)
        return flask.render_template(
            template or self.read_template, view=self, **kwargs)

    def delete(self, template=None, redirect=None, **kwargs):
        """Delete an entry from the database.

        :param template: The template you want to render
        :type template: str

        :param redirect: The URL where you want to redirect after the function
        :type redirect: str, func(lambda)

        """
        if flask.request.method == 'POST':
            self.session.delete(self.data)
            self.session.commit()
            if redirect in ACTIONS:
                redirect = self.action_url_for(redirect)
            return flask.redirect(
                redirect or
                self.action_url_for(
                    self.list_endpoint or
                    self.table_endpoint))
        return flask.render_template(
            template or self.delete_template, view=self, **kwargs)
