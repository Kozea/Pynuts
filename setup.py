from setuptools import setup

import pynuts

setup(
    name="Pynuts",
    version=pynuts.__version__,
    url="http://www.pynuts.org/",
    license="BSD",
    platforms="Any",
    packages=["pynuts"],
    package_data={'pynuts': ['templates/_pynuts/*.jinja2',
                             'static/javascript/*.js']},
    install_requires=[
        'Flask-SQLAlchemy', 'Flask-WTF', 'Flask-WeasyPrint', 'docutils',
        'dulwich', 'docutils_html5_writer', 'Flask-Uploads']
)
