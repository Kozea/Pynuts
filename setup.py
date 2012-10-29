from setuptools import setup

setup(
    name="Pynuts",
    version="0.1",
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
