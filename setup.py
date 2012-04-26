from setuptools import setup

setup(
    name="Pynuts",
    version="0.1",
    url="http://www.pynuts.org/",
    license="GNU GPL v3",
    platforms="Any",
    packages=["pynuts"],
    package_data={'pynuts': ['templates/*.jinja2']},
    install_requires=[
        'flask-sqlalchemy', 'flask-wtf', 'weasyprint', 'docutils', 'dulwich']
)
