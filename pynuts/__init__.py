"""__init__ file for Pynuts."""

import flask
from flask.ext.sqlalchemy import SQLAlchemy

import document
import view
import rights


class Pynuts(flask.Flask):
    """Create the Pynuts class.

    :param import_name: Flask application name
    :param config: Flask application configuration
    :param reflect: Create models with database data

    .. seealso::
      `Flask Application <http://flask.pocoo.org/docs/api/>`_

    """
    def __init__(self, import_name, config=None, reflect=False,
                 *args, **kwargs):
        super(Pynuts, self).__init__(import_name, *args, **kwargs)
        self.config.update(config or {})
        self.db = SQLAlchemy(self)
        self.documents = {}
        if reflect:
            self.db.metadata.reflect(bind=self.db.get_engine(self))

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

    def render_rest(self, document_type, part='index.rst.jinja2',
                    **kwargs):
        return self.documents[document_type].generate_rest(part, **kwargs)
