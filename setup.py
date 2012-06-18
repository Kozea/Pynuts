from setuptools import setup

setup(
    name="Pynuts",
    version="0.1",
    url="http://www.pynuts.org/",
    license="GNU GPL v3",
    platforms="Any",
    packages=["pynuts"],
    package_data={'pynuts': ['templates/*.jinja2', 'static/javascript/*.js']},
    install_requires=[
        'flask-sqlalchemy', 'flask-wtf', 'weasyprint', 'docutils', 'dulwich',
        'docutils_html5_writer']
)
