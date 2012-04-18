import docutils
from weasyprint import HTML
from docutils.writers.html4css1 import Writer
import docutils.core
from tempfile import NamedTemporaryFile
from flask import send_file
import jinja2


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

    def generate_HTML(self, part, **kwargs):
        source = self.environment.get_template(
            self.path.format(**kwargs)).render(
            **kwargs).encode('utf-8')
        parts = docutils.core.publish_parts(
            source=source, writer=Writer(),
            settings_overrides=self.settings)
        text = parts[part].encode('utf-8')
        return text

    def generate_PDF(self, **kwargs):
        html = self.generate_HTML(part='whole', **kwargs)
        return HTML(string=html).write_pdf(stylesheets=self.css)

    def download_PDF_attachment(self, attachment_filename=None, **kwargs):
        temp_file = NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(self.generate_PDF(**kwargs))
        return send_file(temp_file.name, as_attachment=True,
                         attachment_filename=attachment_filename)
