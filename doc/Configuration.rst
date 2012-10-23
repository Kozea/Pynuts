Configuration file
==================

Configuration values
--------------------

`CSRF_ENABLED`
    This is used by WTForms, see `WTForms documentation <http://packages.python.org/Flask-WTF>`_

`SQLALCHEMY_DATABASE_URI``
    The URI to your database. For example: ``sqlite:////tmp/test.db'``.

`PYNUTS_DOCUMENT_REPOSITORY`
    The path to the document repository.
    If you supply a relative path, it will be taken relatively to the app instance folder. See `Flask documentation <http://flask.pocoo.org/docs/config/#instance-folders>`_.
    If you do not supply anything, the document repository will be stored in a `documents.git` folder, placed in the app instance folder.


Specific configuration file
---------------------------

You can launch your pynuts application with a specific configuration file.

To do that, simply run your executable with `-c` or `--config` providing the name of your configuration file::

    $ python executable.py -c config_file
    * Running on http://127.0.0.1:5000/

.. warning::

    The config file has to be located in the same directory than the executable.
