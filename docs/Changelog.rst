Pynuts changelog
================

Here you can see the full list of changes between each Pynuts release.

Version 0.3
-----------
* The ``pynuts.Pynuts`` class no longer inherits from ``flask.Flask``.
* The ``SQLAlchemy`` ORM object is stored in the ``Flask`` app, and not in the ``Pynuts`` object.
* The Pynuts document repository is only initialised when needed for the first time, instead of in the ``pynuts.Pynuts.__init__`` method.


Version 0.2
-----------
First stable public release version.