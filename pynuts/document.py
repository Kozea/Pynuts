"""Document file for Pynuts."""

import docutils
from weasyprint import HTML
from docutils.writers.html4css1 import Writer
import docutils.core
from tempfile import NamedTemporaryFile
from flask import (
    send_file, safe_join, render_template, request, redirect, flash)
import jinja2
import os
import shutil
from environment import JINJA2_ENVIRONMENT


class MetaDocument(type):
    """Metaclass for document classes."""
    def __init__(metacls, name, bases, dict_):
        if metacls.folder:
            metacls.environment = jinja2.Environment(
                 loader=jinja2.FileSystemLoader(metacls.folder))
        super(MetaDocument, metacls).__init__(name, bases, dict_)


class Document(object):
    """This class represents a document object. """
    __metaclass__ = MetaDocument

    environment = None

    #: Docutils settings
    settings = {}

    #: Document Stylesheet
    css = None

    #: Path to the source model
    model = None

    #: Destination folder of instance document
    folder = None

    #: Path to the model filename. Could be a python string format
    path = None

    #: Name of the model
    index = 'index.rst.jinja2'

    # Templates
    edit_template = 'edit_document.jinja2'
    html_document = 'html_document.jinja2'

    @classmethod
    def get_path(cls, **kwargs):
        """Return the complete path to the filename with safety."""
        return os.path.join(cls.folder,
            safe_join(cls.path.format(**kwargs), cls.index))

    @classmethod
    def get_rst(cls, **kwargs):
        """Return the ReST content of the document."""
        with open(cls.get_path(**kwargs), 'r') as stream:
            return stream.read()

    @classmethod
    def generate_HTML(cls, part, **kwargs):
        """Generate the HTML of the document.

        :param part: part of the document to generate
        :type part: String

        .. seealso::
            `Docutils writer publish parts \
            <http://docutils.sourceforge.net/docs/api/publisher.html\
            #publish-parts-details>`_

        """
        source = cls.environment.get_template(
            safe_join(cls.path.format(**kwargs), cls.index),
            parent=cls.folder).render(
            **kwargs).encode('utf-8')
        parts = docutils.core.publish_parts(
            source=source, writer=Writer(),
            settings_overrides=cls.settings)
        text = parts[part].encode('utf-8')
        return text

    @classmethod
    def generate_PDF(cls, **kwargs):
        """Generate PDF from the document."""
        html = cls.generate_HTML(part='whole', **kwargs)
        return HTML(string=html).write_pdf(stylesheets=cls.css)

    @classmethod
    def download_PDF(cls, filename=None, **kwargs):
        """Return PDF file in attachment.

        :param filename: set the filname attachment.
        :type filename: String

        """
        temp_file = NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(cls.generate_PDF(**kwargs))
        return send_file(temp_file.name, as_attachment=True,
                         attachment_filename=filename)

    @classmethod
    def create(cls, **kwargs):
        """Create instance ReST model document and its resources."""
        path = safe_join(cls.folder, cls.path.format(**kwargs))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        shutil.copytree(cls.model, path)

    @classmethod
    def edit(cls, template=None, redirect_url=None, **kwargs):
        """Return the template where you can edit the ReST document.

        :param template: the view application template
        :type template: String

        :param redirect_url: the route to go after saving
        :type redirect_url: String

        """
        if request.method == 'POST':
            with open(cls.get_path(**kwargs), 'w') as stream:
                stream.write(request.form['document'].encode('utf-8'))
            flash('Document was saved.', 'ok')
            if redirect_url:
                return redirect(redirect_url)
        return render_template(template, cls=cls, **kwargs)

    @classmethod
    def view_edit(cls, **kwargs):
        """Render the HTML for edit_template."""
        template = JINJA2_ENVIRONMENT.get_template(cls.edit_template)
        text = cls.get_rst(**kwargs).decode('utf-8')
        return jinja2.Markup(template.render(cls=cls, text=text, **kwargs))

    @classmethod
    def html(cls, template=None, **kwargs):
        """Return the HTML document template.

        :param template: the view application template
        :type template: String

        """
        return render_template(template, cls=cls, **kwargs)

    @classmethod
    def view_html(cls, part='html_body', **kwargs):
        """Render the HTML for html_document.

        :param part: part of the document to generate
        :type part: String

        .. seealso::
            `Docutils writer publish parts \
            <http://docutils.sourceforge.net/docs/api/publisher.html\
            #publish-parts-details>`_

        """
        template = JINJA2_ENVIRONMENT.get_template(cls.html_document)
        text = cls.generate_HTML(part=part, **kwargs).decode('utf-8')
        return jinja2.Markup(template.render(cls=cls, text=text, **kwargs))
