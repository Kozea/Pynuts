"""Init file for koztumize tests"""
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import sqlite3
from tempfile import mkdtemp
from contextlib import closing

PATH = os.path.dirname(os.path.dirname(__file__))
TEMP_DIR = None
DATABASE = '/tmp/test.db'

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
    # global variable shouldn't be used but is quite useful here
    # pylint: disable=W0603
    global TEMP_DIR
    TEMP_DIR = mkdtemp()
    if os.path.exists(os.path.join(PATH, 'tests', 'fake_instance')):
        shutil.rmtree(os.path.join(PATH, 'tests', 'fake_instance'))
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    app = pynuts.Pynuts('complete',
        config={'PYNUTS_DOCUMENT_REPOSITORY': os.path.join(
                    PATH, 'tests', 'fake_instance', 'documents.git')},
        config_file='config/test.cfg',
        reflect=True)
    application.app = app
    import complete.executable
    execute_sql(application.app, 'database.sql')


def teardown_fixture():
    """Remove the temp directory after the tests."""
    if os.path.exists(os.path.join(PATH, 'tests', 'fake_instance')):
        shutil.rmtree(os.path.join(PATH, 'tests', 'fake_instance'))
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    execute_sql(application.app, 'drop_all.sql')


def setup_func():
    execute_sql(application.app, 'insert_data.sql')
    shutil.copytree(
        os.path.join(PATH, 'tests', 'dump', 'instance', 'documents.git'),
        os.path.join(PATH, 'tests', 'fake_instance', 'documents.git'))


def teardown_func():
    execute_sql(application.app, 'truncate_all.sql')
    shutil.rmtree(os.path.join(PATH, 'tests', 'fake_instance'))
