"""__init__ file for Pynuts."""

import flask
from flask.ext.sqlalchemy import SQLAlchemy


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
        if reflect:
            self.db.metadata.reflect(bind=self.db.get_engine(self))
