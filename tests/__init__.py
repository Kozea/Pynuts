"""Init file for koztumize tests"""
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import sqlite3
from tempfile import mkdtemp, mkstemp
from contextlib import closing

PATH = os.path.dirname(os.path.dirname(__file__))
DATABASE = mkstemp()[1]

sys.path.insert(0, os.path.join(PATH, 'doc', 'example'))
sys.path.insert(0, PATH)

import pynuts
from complete import application


def execute_sql(application, filename, folder=None):
    """Execute a sql file in the sql folder for application.app"""
    path = os.path.join(PATH, 'tests', 'sql', filename)
    with closing(sqlite3.connect(DATABASE)) as db:
        with application.open_resource(path) as f:
            db.cursor().executescript(f.read())
        db.commit()


def setup_fixture():
    """Setup function for tests."""
    app = pynuts.Pynuts('complete',
        config={
            'PYNUTS_DOCUMENT_REPOSITORY': os.path.join(
                mkdtemp(), 'documents.git'),
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + DATABASE},
        config_file='config/test.cfg',
        reflect=True)
    application.app = app
    import complete.executable


def teardown_fixture():
    """Remove the temp directory after the tests."""
    os.rmdir(os.path.dirname(
        application.app.config['PYNUTS_DOCUMENT_REPOSITORY']))


def setup_func():
    execute_sql(application.app, 'database.sql')
    shutil.copytree(
        os.path.join(PATH, 'tests', 'dump', 'instance', 'documents.git'),
        application.app.config['PYNUTS_DOCUMENT_REPOSITORY'])


def teardown_func():
    os.remove(DATABASE)
    shutil.rmtree(application.app.config['PYNUTS_DOCUMENT_REPOSITORY'])