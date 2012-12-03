Pynuts changelog
================

Here you can see the full list of changes between each Pynuts release.

Version 0.4
-----------
* Simplification of crud functions
* Handle permissions on links with auth_url_for with request/link params in acl rights functions
* Rewrite of the action_url_for


Version 0.3
-----------
* The ``pynuts.Pynuts`` class no longer inherits from ``flask.Flask``.
* Pynuts no longer handles configuration. It uses Flask’s ``app.config``.
* Pynuts no longer create a Flask-SQLAlchemy object. Applications are
  expected to do that themselves.
* The Pynuts document repository is only initialised when needed for the first time, instead of in the ``pynuts.Pynuts.__init__`` method.
* The ``pynuts.view.FormBase`` is now called ``pynuts.view.BaseForm``
* When declaring a Form class in a pynuts model, you can make it inherit from ``pynuts.view.BaseForm``, or from your own form class.


Version 0.2
-----------
First stable public release version.
