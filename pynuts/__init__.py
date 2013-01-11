"""__init__ file for Pynuts."""

__version__ = '0.4.2'

import os
import sys
import flask
from werkzeug.utils import cached_property
from flask.ext.uploads import configure_uploads, patch_request_class
from dulwich.repo import Repo

from .environment import alter_environment
from . import document, rights, view
from .view import auth_url_for


class Pynuts(object):
    """Create the Pynuts class

    :param app: a Flask application object
    :type app: flask.Flask

    .. seealso::
      `Flask Application <http://flask.pocoo.org/docs/api/>`_

    """
    def __init__(self, app, authed_url_for=False):

        self.app = app

        # Pynuts default config
        # Can be overwritten by setting
        # these parameters in the application config
        self.app.config.setdefault('CSRF_ENABLED', False)
        self.app.config.setdefault('UPLOADS_DEFAULT_DEST',
                                   os.path.join(app.instance_path, 'uploads'))
        self.app.config.setdefault('PYNUTS_DOCUMENT_REPOSITORY',
                                   'documents.git')

        self.documents = {}
        self.views = {}

        # Serve files from the Pynuts static folder
        # at the /_pynuts/static/<path:filename> URL
        self.app.add_url_rule('/_pynuts/static/<path:filename>',
                              '_pynuts-static', static)

        class Document(document.Document):
            """Document base class of the application."""
            _pynuts = self
            _app = self.app

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
            # Create a new Jinja2 environment with Pynuts helpers
            environment = self.app.jinja_env

        alter_environment(self.app.jinja_env)

        self.app.jinja_env.globals.update({'pynuts': self})
        self.app.jinja_env.globals.update({'auth_url_for': auth_url_for})
        if authed_url_for:
            self.app.jinja_env.globals.update({'url_for': auth_url_for})

        self.ModelView = ModelView

        self.app.before_request(self.create_context)

    @cached_property
    def document_repository(self):
        """ Return the application bare git document repository.

            If the application has a `PYNUTS_DOCUMENT_REPOSITORY`
            configuration key expressed as an absolute path, the repo
            will be located at this path. If this configuration key
            is expressed as a relative path, its location will be taken
            relatively to the application instance path.
            Finally, if no such configuration is found, a bare git
            repository will be created in the `documents.git` directory,
            located at the application instance path.

            All parent directories will be created if needed, and if
            non-existent, the repository will be initialized.
        """
        self.document_repository_path = (
            os.path.join(
                self.app.instance_path,
                self.app.config.get('PYNUTS_DOCUMENT_REPOSITORY')))
        # If document_repository_path does not exist,
        # create it (and possible parent folders) and initialize the bare repo
        if os.path.exists(self.document_repository_path):
            return Repo(self.document_repository_path)
        else:
            os.makedirs(self.document_repository_path)
            return Repo.init_bare(self.document_repository_path)

    def render_rest(self, document_type, part='index.rst.jinja2',
                    **kwargs):
        """Return the generated ReST version of the document."""
        return self.documents[document_type].generate_rest(part, **kwargs)

    def create_context(self):
        """Create the request context."""
        flask.g.context = self._context_class()

    def add_upload_sets(self, upload_sets, upload_max_size=16777216):
        """Configure the app with the argument upload sets."""
        configure_uploads(self.app, upload_sets)
        # Limit the size of uploads to 16MB
        patch_request_class(self.app, upload_max_size)


def static(filename):
    """ Return files from Pynuts static folder.

    :param filename: the basename of the file contained in Pynuts static folder
    """
    return flask.send_from_directory(
        os.path.join(os.path.dirname(__file__), 'static'), filename)


def install_secret_key(app, filename='secret_key'):
    """Configure the SECRET_KEY from a file in the instance directory.

    If the file does not exist, print instructions to create it from a shell
    with a random key, then exit.

    """
    filename = os.path.join(app.instance_path, filename)
    try:
        app.config['SECRET_KEY'] = open(filename, 'rb').read()
    except IOError:
        print 'Error: No secret key. Create it with:'
        if not os.path.isdir(os.path.dirname(filename)):
            print 'mkdir -p', os.path.dirname(filename)
        print 'head -c 24 /dev/urandom >', filename
        sys.exit(1)
