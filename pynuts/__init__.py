import flask
from flaskext.sqlalchemy import SQLAlchemy


class Pynuts(flask.Flask):
    def __init__(self, *args, **kwargs):
        config = kwargs.pop('config', {})
        super(Pynuts, self).__init__(*args, **kwargs)
        self.config.update(config)
        self.db = SQLAlchemy(self)
        self.db.metadata.reflect(bind=self.db.get_engine(self))
        self.db.Model._session = self.db.session
