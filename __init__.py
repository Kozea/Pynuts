import flask
import jinja2
import database
from sqlalchemy.orm import class_mapper
from sqlalchemy.util import classproperty


JINJA2_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.PackageLoader('pynuts', 'templates'))
JINJA2_ENVIRONMENT.globals = {'url_for': flask.url_for}


class ModelView(object):
    _mapping = None

    model = None
    form = None

    # Endpoints
    add_endpoint = None
    edit_endpoint = None
    delete_endpoint = None

     # Templates
    view_template = 'view.jinja2'
    list_template = 'list.jinja2'
    table_template = 'table.jinja2'
    edit_template = 'edit.jinja2'
    create_template = 'create.jinja2'

    # Columns
    view_columns = None
    list_column = None
    table_columns = None
    edit_columns = None
    create_columns = None

    def __init__(self, keys):
        self.data = self.model.query.get_or_404(keys)

    @classproperty
    def mapping(cls):
        if not cls._mapping:
            cls._mapping = class_mapper(cls.model)
        return cls._mapping

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
    def view_list(cls):
        columns = cls.list_column or [
            column.key for column in cls.mapping.columns]
        elements = [
            cls([getattr(element, column.key)
                 for column in cls.mapping.primary_key])
            for element in cls.model.query.all()]
        template = JINJA2_ENVIRONMENT.get_template(
            cls.list_template)
        return jinja2.Markup(template.render(
            elements=elements, columns=columns))

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
        if flask.request.method == 'GET':
            cls.form.process()
            return flask.render_template(
                template, cls=cls, *args, **kwargs)
        elif flask.request.method == 'POST':
            cls.form.process(flask.request.form)
            data = cls.model(**dict(flask.request.form.items()))
            database.db.session.add(data)
            database.db.session.commit()
            return flask.redirect(flask.url_for(redirect))

    def edit(self, template=None, redirect=None, *args, **kwargs):
        if flask.request.method == 'GET':
            self.form.process(obj=self.data)
            return flask.render_template(
                template, object=self, *args, **kwargs)
        elif flask.request.method == 'POST':
            self.form.process(flask.request.form, obj=self.data)
            for key, value in flask.request.form.items():
                setattr(self.data, key, value)
            database.db.session.commit()
            return flask.redirect(flask.url_for(redirect))

    def delete(self, redirect=None):
        database.db.session.delete(self.data)
        database.db.session.commit()
        return flask.redirect(flask.url_for(redirect))

    def view(self, template=None, *args, **kwargs):
        self.form.process(obj=self.data)
        return flask.render_template(
            template, obj=self, *args, **kwargs)
