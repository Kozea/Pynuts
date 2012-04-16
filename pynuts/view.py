import flask
import jinja2
from sqlalchemy.orm import class_mapper
from sqlalchemy.util import classproperty

JINJA2_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.PackageLoader('pynuts', 'templates'))
JINJA2_ENVIRONMENT.globals.update({'url_for': flask.url_for})


class MetaView(type):
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
    __metaclass__ = MetaView

    _mapping = None

    model = None
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

    def __init__(self, keys=None, element=None):
        if keys:
            self.data = self.model.query.get_or_404(keys)
        elif element:
            self.data = element
        self.form = self.Form(flask.request.form, obj=self.data)

    @classmethod
    def all(cls):
        for element in cls.model.query.all():
            yield cls(element=element)

    @classproperty
    def session(cls):
        return cls.model.query.session

    @staticmethod
    def _get_form_attributes(form):
        return {
            key: form[key].data for key in flask.request.form}

    @classmethod
    def edit_page(cls, function):
        cls.edit_endpoint = function.__name__
        return function

    @classmethod
    def add_page(cls, function):
        cls.add_endpoint = function.__name__
        return function

    @classmethod
    def delete_page(cls, function):
        cls.delete_endpoint = function.__name__
        return function

    @classmethod
    def view_page(cls, function):
        cls.view_endpoint = function.__name__
        return function

    @classmethod
    def view_list(cls):
        template = JINJA2_ENVIRONMENT.get_template(cls.list_template)
        return jinja2.Markup(template.render(cls=cls))

    def view_object(self):
        template = JINJA2_ENVIRONMENT.get_template(self.view_template)
        return jinja2.Markup(template.render(obj=self))

    @classmethod
    def view_table(cls):
        template = JINJA2_ENVIRONMENT.get_template(cls.table_template)
        return jinja2.Markup(template.render(cls=cls))

    @classmethod
    def view_create(cls):
        template = JINJA2_ENVIRONMENT.get_template(cls.create_template)
        return jinja2.Markup(template.render(cls=cls))

    def view_edit(self):
        template = JINJA2_ENVIRONMENT.get_template(self.edit_template)
        return jinja2.Markup(template.render(obj=self))

    @classmethod
    def create(cls, template=None, redirect=None, *args, **kwargs):
        form = cls.Form(flask.request.form)
        if form.validate_on_submit():
            obj = cls(element=cls.model(**cls._get_form_attributes(form)))
            cls.session.add(obj.data)
            cls.session.commit()
            return flask.redirect(flask.url_for(redirect))
        return flask.render_template(template, cls=cls, *args, **kwargs)

    @classmethod
    def list(cls, template=None, *args, **kwargs):
        return flask.render_template(template, cls=cls, *args, **kwargs)

    @classmethod
    def table(cls, template=None, *args, **kwargs):
        return flask.render_template(template, cls=cls, *args, **kwargs)

    def edit(self, template=None, redirect=None, *args, **kwargs):
        if self.form.validate_on_submit():
            for key, value in self._get_form_attributes(self.form).items():
                setattr(self.data, key, value)
            self.session.commit()
            return flask.redirect(flask.url_for(redirect))
        return flask.render_template(template, obj=self, *args, **kwargs)

    def delete(self, redirect=None):
        self.session.delete(self.data)
        self.session.commit()
        return flask.redirect(flask.url_for(redirect))

    def view(self, template=None, *args, **kwargs):
        self.form.process(obj=self.data)
        return flask.render_template(
            template, obj=self, *args, **kwargs)

    @property
    def primary_keys(self):
        return {
            column.key: getattr(self.data, column.key)
            for column in self._mapping.primary_key}
