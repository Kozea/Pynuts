from distutils.core import setup

setup(
    name="Pynuts",
    url="http://www.pynuts.org/",
    license="GNU GPL v3",
    platforms="Any",
    packages=["pynuts"],
    package_data={'pynuts': ['templates/*.jinja2']},
    provides=["pynuts"]
)
