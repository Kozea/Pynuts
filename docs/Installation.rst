Installation
============

Install Pynuts
--------------

You can install Pynuts with easy_install::

    $ easy_install Pynuts

or alternatively if you have pip installed::

    $ pip install Pynuts

We also encourage you to install Pynuts in a virtualenv.

.. warning::

    Pynuts relies on `WeasyPrint <https://github.com/Kozea/WeasyPrint>`_ to generate PDF documents
    from from web documents (HTML, CSS, SVG, etc).
    Some of its dependencies, `pygobject <https://github.com/alexef/pygobject>`_ and
    `pycairo <http://www.cairographics.org/pycairo/>`_  cannot be installed with pip.
    You thus need to perform a system-wide install of these packages, and create the virtualenv
    with the ``--system-site-packages`` option.
    See `the WeasyPrint 'install' page <http://weasyprint.org/docs/install/>`_ for more information.


Github
------

Check out the development version on `Github <https://github.com/Kozea/Pynuts>`_ ::

    $ git clone git://github.com/Kozea/Pynuts

