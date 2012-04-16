import flask
from flask.ext.sqlalchemy import SQLAlchemy


class Pynuts(flask.Flask):
    def __init__(self, import_name, config=None, reflect=False,
                 *args, **kwargs):
        super(Pynuts, self).__init__(import_name, *args, **kwargs)
        self.config.update(config or {})
        self.db = SQLAlchemy(self)
        if reflect:
            self.db.metadata.reflect(bind=self.db.get_engine(self))
