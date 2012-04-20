import docutils
from weasyprint import HTML
from docutils.writers.html4css1 import Writer
import docutils.core
from tempfile import NamedTemporaryFile
from flask import send_file, safe_join
import jinja2
import os
import shutil


class MetaDocument(type):
    """Metaclass for document classes."""
    def __init__(metacls, name, bases, dict_):
        if metacls.folder:
            metacls.environment = jinja2.Environment(
                 loader=jinja2.FileSystemLoader(metacls.folder))
        super(MetaDocument, metacls).__init__(name, bases, dict_)


class Document(object):
    __metaclass__ = MetaDocument

    settings = {}
    css = None
    folder = None
    environment = None
    path = None
    model = None

    @classmethod
    def generate_HTML(cls, part, **kwargs):
        source = cls.environment.get_template(
            cls.path.format(**kwargs), parent=cls.folder).render(
            **kwargs).encode('utf-8')
        parts = docutils.core.publish_parts(
            source=source, writer=Writer(),
            settings_overrides=cls.settings)
        text = parts[part].encode('utf-8')
        return text

    @classmethod
    def generate_PDF(cls, **kwargs):
        html = cls.generate_HTML(part='whole', **kwargs)
        return HTML(string=html).write_pdf(stylesheets=cls.css)

    @classmethod
    def download_PDF_attachment(cls, attachment_filename=None, **kwargs):
        temp_file = NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(cls.generate_PDF(**kwargs))
        return send_file(temp_file.name, as_attachment=True,
                         attachment_filename=attachment_filename)

    @classmethod
    def create(cls, **kwargs):
        path = safe_join(cls.folder, cls.path.format(**kwargs))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        shutil.copytree(cls.model, path)
