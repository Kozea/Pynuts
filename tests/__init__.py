# -*- coding: utf-8 -*-

"""Init file for Pynuts tests"""

import os
import sys
import shutil
import sqlite3
from tempfile import mkdtemp, mkstemp
from contextlib import closing
import flask

from flask_sqlalchemy import SQLAlchemy

PYNUTS_ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
DATABASE = mkstemp()[1]

sys.path.insert(0, PYNUTS_ROOT)
import pynuts
from pynuts import model

sys.path.insert(0, os.path.join(PYNUTS_ROOT, 'docs', 'example'))
from complete import application


def execute_sql(app, filename):
    """Execute a sql file in the sql folder for application.app"""
    path = os.path.join(PYNUTS_ROOT, 'tests', 'sql', filename)
    with closing(sqlite3.connect(DATABASE)) as database:
        with app.open_resource(path) as sql_script:
            database.cursor().executescript(sql_script.read())
        database.commit()


def setup_fixture():
    """Setup function for tests."""
    app = flask.Flask('complete')
    app.config.from_pyfile('config/test.cfg')
    app.config.update({
            'PYNUTS_DOCUMENT_REPOSITORY': os.path.join(mkdtemp(), 'documents.git'),
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + DATABASE,
                }
            )
    app.db = SQLAlchemy(app)
    model.reflect(app)
    application.app = app
    application.nuts = pynuts.Pynuts(app)
    import complete.executable


def teardown_fixture():
    """Remove the temp directory after the tests."""
    shutil.rmtree(os.path.dirname(
        application.app.config['PYNUTS_DOCUMENT_REPOSITORY']))


def setup_func():
    """ Execute the database creation script and remove old Git Bare repo,
        created during app setup or last test.
    """
    execute_sql(application.app, 'database.sql')
    # Delete previous Git Bare repo, created during the setup or the last test
    shutil.rmtree(application.app.config['PYNUTS_DOCUMENT_REPOSITORY'])
    shutil.copytree(
        os.path.join(
            PYNUTS_ROOT, 'tests', 'dump', 'instance', 'documents.git'),
            application.app.config['PYNUTS_DOCUMENT_REPOSITORY'])


def teardown_func():
    """ Remove the temporary database. """
    os.remove(DATABASE)
