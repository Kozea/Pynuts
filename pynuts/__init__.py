"""__init__ file for Pynuts."""

import flask
from flask.ext.sqlalchemy import SQLAlchemy


class Pynuts(flask.Flask):
    """Create the Pynuts class."""
    def __init__(self, import_name, config=None, reflect=False,
                 *args, **kwargs):
        super(Pynuts, self).__init__(import_name, *args, **kwargs)
        self.config.update(config or {})
        self.db = SQLAlchemy(self)
        if reflect:
            self.db.metadata.reflect(bind=self.db.get_engine(self))

    @property
    def Model(self):
        cls = self.db.Model
        cls.db = self.db
        return cls
