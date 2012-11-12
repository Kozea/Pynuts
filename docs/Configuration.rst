Configuration
=============

Configuration keys
------------------

`PYNUTS_DOCUMENT_REPOSITORY`
    The path to the document repository.

    If you supply a relative path, it will be taken relatively to the Flask app instance folder (see `Flask documentation <http://flask.pocoo.org/docs/config/#instance-folders>`_).
    If you do not supply anything, the document repository will be stored in a `documents.git` folder, placed in the app instance folder.

`UPLOADS_DEFAULT_DEST`
    The path to the uploads root directory.

    If you set this, then if an upload set’s destination isn’t otherwise declared, then its uploads will be stored in a subdirectory of this directory. For example, if you set this to /var/uploads, then a set named photos will store its uploads in /var/uploads/photos.

    The default value is `instance/uploads`, where instance is the Flask app instance folder.

Specific configuration file
---------------------------

You can launch your pynuts application with a specific configuration file.

To do that, simply run your executable with `-c` or `--config` providing the name of your configuration file::

    $ python executable.py -c config_file
    * Running on http://127.0.0.1:5000/

.. warning::

    The config file has to be located in the same directory than the executable.
