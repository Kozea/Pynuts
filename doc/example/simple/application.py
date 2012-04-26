import pynuts

CONFIG = {
        'CSRF_ENABLED': False,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db'}

app = pynuts.Pynuts(__name__, config=CONFIG)
