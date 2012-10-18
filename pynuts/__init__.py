"""__init__ file for Pynuts."""

import os
import flask
from werkzeug import cached_property
from flask.ext.sqlalchemy import SQLAlchemy

from . import document, git, rights, view, filters
from .environment import create_environment


class Pynuts(flask.Flask):
    """Create the Pynuts class.

    :param import_name: Flask application name
    :type import_name: str
    :param config: Flask application configuration
    :type config: dict
    :param config_file: path of the application configuration file
    :type config_file: str
    :param reflect: Create models with database data
    :type reflect: bool

    .. seealso::
      `Flask Application <http://flask.pocoo.org/docs/api/>`_

    """
    def __init__(self, import_name, config=None, config_file=None,
                 reflect=False, *args, **kwargs):
        super(Pynuts, self).__init__(import_name, *args, **kwargs)

        self.config['CSRF_ENABLED'] = False
        if config_file:
            self.config.from_pyfile(config_file)
        if config:
            self.config.update(config)

        self.db = SQLAlchemy(self)
        self.documents = {}
        self.views = {}

        if reflect:
            self.db.metadata.reflect(bind=self.db.get_engine(self))

        self.document_repository_path = (
            self.config.get('PYNUTS_DOCUMENT_REPOSITORY') or
            os.path.join(self.instance_path, 'documents.git'))

        self.add_url_rule('/_pynuts/static/<path:filename>',
                          '_pynuts-static', static)

        class Document(document.Document):
            """Document base class of the application."""
            _pynuts = self

        self.Document = Document

        class Context(object):
            """Context base class of the application.

            You can get or set any element in the context stored in
            the `g` flask object.

            Example : Set the current time of the request in the context, using
            datetime :

            @app.before_request
            def set_request_time():
                g.context.request_time = datetime.now().strftime('%Y/%m/%d')

            """
            __metaclass__ = rights.MetaContext
            _pynuts = self

            def __getitem__(self, key):
                return getattr(self, key)

            def __setitem__(self, key, value):
                setattr(self, key, value)

            def get(self, key, default=None):
                return getattr(self, key, default)

        self.Context = Context

        class ModelView(view.ModelView):
            """Model view base class of the application."""
            _pynuts = self
            environment = create_environment(_pynuts.jinja_env.loader)

        self.ModelView = ModelView

        self.before_request(self.create_context)

    @cached_property
    def document_repository(self):
        """Return the path to the document repository."""
        return git.Repo(self.document_repository_path)

    def render_rest(self, document_type, part='index.rst.jinja2',
                    **kwargs):
        """Return the rest of the document."""
        return self.documents[document_type].generate_rest(part, **kwargs)

    def create_context(self):
        """Create the request context."""
        flask.g.context = self._context_class()


def static(filename):
    """Return files from Pynuts static folder."""
    return flask.send_from_directory(
        os.path.join(os.path.dirname(__file__), 'static'), filename)
