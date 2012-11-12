import re
import os
from setuptools import setup

VERSION = re.search("__version__ = '([^']+)'", open(
    os.path.join(os.path.dirname(__file__), 'pynuts', '__init__.py')
).read().strip()).group(1)

setup(
    name="Pynuts",
    author="Kozea",
    version=VERSION,
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
