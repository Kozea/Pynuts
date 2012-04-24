"""__init__ file for Pynuts."""

import flask
from flask.ext.sqlalchemy import SQLAlchemy

import document
import view


class Pynuts(flask.Flask):
    """Create the Pynuts class."""
    def __init__(self, import_name, config=None, reflect=False,
                 *args, **kwargs):
        super(Pynuts, self).__init__(import_name, *args, **kwargs)
        self.config.update(config or {})
        self.db = SQLAlchemy(self)
        if reflect:
            self.db.metadata.reflect(bind=self.db.get_engine(self))

        class Document(document.Document):
            """Document base class of the application."""
            _pynuts = self

        self.Document = Document

        class ModelView(view.ModelView):
            """Model view base class of the application."""
            _pynuts = self

        self.ModelView = ModelView
