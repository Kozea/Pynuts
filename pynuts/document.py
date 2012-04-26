import os
import docutils
import jinja2
import docutils.core
import mimetypes
from tempfile import NamedTemporaryFile
from flask import Response, render_template, request, redirect, flash, url_for
from werkzeug.datastructures import Headers
from jinja2 import ChoiceLoader
from weasyprint import HTML
from docutils.writers.html4css1 import Writer

from .environment import create_environment
from .fs import GitFS, GitLoader


class MetaDocument(type):
    """Metaclass for document classes."""
    def __init__(cls, name, bases, dict_):
        if cls.repository:
            # TODO: find a better endpoint name than the name of the class
            cls._resource = cls.__name__
            cls._pynuts.add_url_rule(
                '/_resource/%s/<document_id>/<version>/<path:filename>' % (
                    cls._resource),
                cls._resource, cls.static_route)
            if not os.path.isabs(cls.model):
                cls.model = os.path.join(cls._pynuts.root_path, cls.model)
            if cls.settings is None:
                cls.settings = {}
            super(MetaDocument, cls).__init__(name, bases, dict_)


class Document(object):
    """Class Document."""
    __metaclass__ = MetaDocument

    _resource = None

    settings = None
    css = None
    repository = None
    document_id_template = None
    model = None
    index = 'index.rst.jinja2'

    # Templates
    edit_template = 'edit_document.jinja2'

    def __init__(self, document_id, version=None):
        self.document_id = document_id
        self.git = GitFS(self.repository, branch=document_id, commit=version)
        self.version = self.git.commit.id if self.git.commit else None
        self.environment = create_environment()
        self.environment.loader = ChoiceLoader((
            GitLoader(self.git), self.environment.loader))

    @classmethod
    def from_data(cls, version=None, **kwargs):
        return cls(cls.document_id_template.format(**kwargs), version=version)

    def resource_base64(self, filename, **kwargs):
        """Absolute resource filename."""
        mimetype, _ = mimetypes.guess_type(filename)
        return 'data:%s;base64,%s' % (
            mimetype or '',
            self.git.read(filename).encode('base64').replace('\n', ''))

    def resource_url(self, filename):
        """Resource URL for the application."""
        return url_for(
            self._resource, document_id=self.document_id, filename=filename,
            version=self.version)

    @classmethod
    def static_route(cls, document_id, filename, version):
        """Serve static files for documents."""
        mimetype, _ = mimetypes.guess_type(filename)
        return Response(
            cls(document_id, version).git.read(filename), mimetype=mimetype)

    @classmethod
    def generate_HTML(cls, part, resource_function='url', **kwargs):
        """Generate the HTML of the document.

           You can choose which part of the document you want

           (check docutils writer publish parts)

        """
        document = cls.from_data(**kwargs)
        template = document.environment.get_template(document.index)
        resource = getattr(document, 'resource_%s' % resource_function)
        source = template.render(resource=resource, **kwargs)
        parts = docutils.core.publish_parts(
            source=source, writer=Writer(),
            settings_overrides=document.settings)
        return parts[part]

    @classmethod
    def generate_PDF(cls, **kwargs):
        """Generate PDF from the document."""
        html = cls.generate_HTML(
            part='whole', resource_function='base64', **kwargs)
        # TODO: stylesheets
        return HTML(string=html.encode('utf-8')).write_pdf()

    @classmethod
    def view_html(cls, part='html_body', **kwargs):
        """Render the HTML for html_document.

           You can choose which part of the document you want

           (check docutils writer publish parts)

        """
        return jinja2.Markup(cls.generate_HTML(part=part, **kwargs))

    @classmethod
    def download_PDF(cls, filename=None, **kwargs):
        """Return PDF file in attachment.

           You can set the filname attachment.

        """
        temp_file = NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_file.write(cls.generate_PDF(**kwargs))
        headers = Headers()
        headers.add('Content-Disposition', 'attachment', filename=filename)
        return Response(
            cls.generate_PDF(**kwargs), mimetype='application/pdf',
            headers=headers)

    @classmethod
    def create(cls, **kwargs):
        """Create the ReST document.

        Return ``True`` if the document has been created, ``False`` if the
        document id was already used.

        """
        document = cls.from_data(**kwargs)
        tree_id = document.git.store_directory(cls.model)
        commit_id = document.git.store_commit(
            tree_id, 'Pynuts', 'Create %s' % document.document_id)
        return document.git.repository.refs.add_if_new(
            'refs/documents/%s' % document.document_id, commit_id)

    @classmethod
    def edit(cls, template, redirect_url=None, **kwargs):
        """Return the template where you can edit the ReST document.

        :param template: your application template.
        :param redirect_url: the route you want to go after saving.

        Return ``True`` if the document has been edited, ``False`` if the
        document id was already used.

        """
        if request.method == 'POST':
            document = cls.from_data(
                version=request.form['_old_commit'], **kwargs)
            blob_id = document.git.store_string(
                request.form['document'].encode('utf-8'))
            tree_id = document.git.tree.add(cls.index, 0100644, blob_id)
            commit_id = document.git.store_commit(
                tree_id, 'Pynuts', 'Edit %s' % document.document_id)
            if document.git.repository.refs.set_if_equals(
                'refs/documents/%s' % document.document_id, document.version,
                commit_id):
                flash('The document was saved.', 'ok')
                if redirect_url:
                    return redirect(redirect_url)
            else:
                flash('A conflict happened.', 'error')
        return render_template(template, cls=cls, **kwargs)

    @classmethod
    def view_edit(cls, **kwargs):
        """Render the HTML for edit_template."""
        document = cls.from_data(**kwargs)
        template = document.environment.get_template(cls.edit_template)
        text = document.git.read(cls.index).decode('utf-8')
        return jinja2.Markup(template.render(
            cls=cls, text=text, old_commit=document.git.commit.id, **kwargs))
