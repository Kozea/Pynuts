"""__init__ file for Pynuts."""

import os
import flask
from werkzeug import cached_property
from flask.ext.sqlalchemy import SQLAlchemy

from . import document, git, rights, view


class Pynuts(flask.Flask):
    """Create the Pynuts class.

    :param import_name: Flask application name
    :param config: Flask application configuration
    :param reflect: Create models with database data

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
            """Context base class of the application."""
            __metaclass__ = rights.MetaContext
            _pynuts = self

        self.Context = Context

        class ModelView(view.ModelView):
            """Model view base class of the application."""
            _pynuts = self

        self.ModelView = ModelView

    @cached_property
    def document_repository(self):
        """Return the path to the document repository."""
        return git.Repo(self.document_repository_path)

    def render_rest(self, document_type, part='index.rst.jinja2',
                    **kwargs):
        """Return the rest of the document."""
        return self.documents[document_type].generate_rest(part, **kwargs)


def static(filename):
    """Return files from Pynuts static folder."""
    return flask.send_from_directory(
        os.path.join(os.path.dirname(__file__), 'static'), filename)
