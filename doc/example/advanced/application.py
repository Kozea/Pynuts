import pynuts

CONFIG = {'SQLALCHEMY_DATABASE_URI': 'sqlite:////tmp/test.db',
          'PYNUTS_DOCUMENT_REPOSITORY': '/tmp/employees.git'}

app = pynuts.Pynuts(__name__, config=CONFIG)
