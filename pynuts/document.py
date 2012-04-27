"""Document file for Pynuts."""

import os
import docutils
import jinja2
import docutils.core
import mimetypes
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
            cls._pynuts.documents[cls._resource] = cls
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
    """This class represents a document object. """
    __metaclass__ = MetaDocument

    _resource = None

    #: Jinja Environment
    environment = None

    #: Docutils settings
    settings = None

    #: Git repository
    repository = None

    #: Template id
    document_id_template = None

    #: Model folder
    model = None

    # Templates
    edit_template = 'edit_document.jinja2'

    def __init__(self, document_id, version=None):
        self.document_id = document_id
        self.git = GitFS(self.repository, branch=self.branch, commit=version)
        self.environment = create_environment()
        self.environment.loader = ChoiceLoader((
            GitLoader(self.git), self.environment.loader))
        self.environment.globals['render_rest'] = self._pynuts.render_rest

    @property
    def branch(self):
        """Branch name of the document."""
        return 'refs/documents/%s' % self.document_id

    @property
    def archive_branch(self):
        """Branch name of the document archives."""
        return 'refs/archives/%s' % self.document_id

    @property
    def version(self):
        """Actual git version of the document."""
        return self.git.commit.id

    @property
    def history(self):
        """Yield the parent documents."""
        git = GitFS(self.repository, branch=self.branch)
        for version in git.history():
            yield type(self)(self.document_id, version=version)

    @property
    def archive_history(self):
        """Yield the parent documents stored as archives."""
        git = GitFS(self.repository, branch=self.archive_branch)
        for version in git.history():
            yield type(self)(self.document_id, version=version)

    @classmethod
    def from_data(cls, version=None, **kwargs):
        """Create an instance of the class from the given data."""
        return cls(cls.document_id_template.format(**kwargs), version=version)

    def resource_base64(self, filename, **kwargs):
        """Resource content encoded in base64."""
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
    def generate_rest(cls, part='index.rst.jinja2', resource_type='url',
                      version=None, **kwargs):
        """Generate the ReStructuredText version of the document.

        :param part: part of the document to render.
        :param version: version of the document to render.
        :param resource_type: external resource type: 'url' or 'base64'.

        """
        document = cls.from_data(version=version, **kwargs)
        template = document.environment.get_template(part)
        resource = getattr(document, 'resource_%s' % resource_type)
        return template.render(resource=resource, **kwargs)

    @classmethod
    def generate_html(cls, part='index.rst.jinja2', resource_type='url',
                      version=None, **kwargs):
        """Generate the HTML samples of the document.

        The output is a dict corresponding to the different HTML samples as
        generated by Docutils.

        .. seealso::
           `Docutils writer publish parts
           <http://docutils.sourceforge.net/docs/api/publisher.html\
           #publish-parts-details>`_

        :param part: part of the document to render.
        :param version: version of the document to render.
        :param resource_type: external resource type: 'url' or 'base64'.

        """
        source = cls.generate_rest(
            part=part, version=version, resource_type=resource_type, **kwargs)
        parts = docutils.core.publish_parts(
            source=source, writer=Writer(), settings_overrides=cls.settings)
        return parts

    @classmethod
    def generate_pdf(cls, part='index.rst.jinja2', version=None, **kwargs):
        """Generate the PDF version from the document.

        :param part: part of the document to render.
        :param version: version of the document to render.

        """
        html = cls.generate_html(part, 'base64', **kwargs)['whole']
        # TODO: stylesheets
        return HTML(string=html.encode('utf-8')).write_pdf()

    @classmethod
    def download_pdf(cls, part='index.rst.jinja2', version=None, filename=None,
                     **kwargs):
        """Get a HTTP response with PDF document as file in attachment.

        :param part: part of the document to render.
        :param version: version of the document to render.
        :param filename: attachment filename.

        """
        headers = Headers()
        headers.add('Content-Disposition', 'attachment', filename=filename)
        return Response(
            cls.generate_pdf(part=part, version=version, **kwargs),
            mimetype='application/pdf', headers=headers)

    @classmethod
    def archive(cls, part='index.rst.jinja2', version=None, message=None,
                **kwargs):
        """Archive the given version of the document.

        :param part: part of the document to archive.
        :param version: version of the document to archive.

        """
        document = cls.from_data(version=version, **kwargs)
        blob_id = document.git.store_string(
            document.generate_rest(part=part, **kwargs).encode('utf-8'))
        document.git.tree.add(os.path.splitext(part)[0], 0100644, blob_id)
        document.git.store.add_object(document.git.tree)
        parents = []
        if document.archive_branch in document.git.repository.refs:
            parents.append(
                document.git.repository.refs[document.archive_branch])
        if message is None:
            message = 'Archive %s' % document.document_id
        commit_id = document.git.store_commit(
            document.git.tree.id, parents, 'Pynuts', message)
        document.git.repository.refs[document.archive_branch] = commit_id

    @classmethod
    def create(cls, **kwargs):
        """Create the ReST document.

        Return ``True`` if the document has been created, ``False`` if the
        document id was already used.

        """
        document = cls.from_data(**kwargs)
        tree_id = document.git.store_directory(cls.model)
        commit_id = document.git.store_commit(
            tree_id, None, 'Pynuts', 'Create %s' % document.document_id)
        return document.git.repository.refs.add_if_new(
            document.branch, commit_id)

    @classmethod
    def edit(cls, template, part='index.rst.jinja2', version=None,
             redirect_url=None, **kwargs):
        """Edit the document.

        :param template: application template with edition form.
        :param part: part of the document to edit.
        :param version: version of the document to edit.
        :param redirect_url: route to go after saving.

        Return ``True`` if the document has been edited, ``False`` if the
        document id was already used.

        """
        if request.method == 'POST':
            document = cls.from_data(
                version=request.form['_old_commit'], **kwargs)
            blob_id = document.git.store_string(
                request.form['document'].encode('utf-8'))
            document.git.tree.add(part, 0100644, blob_id)
            document.git.store.add_object(document.git.tree)
            commit_id = document.git.store_commit(
                document.git.tree.id, [document.git.commit.id],
                'Pynuts', 'Edit %s' % document.document_id)
            if document.git.repository.refs.set_if_equals(
                document.branch, document.version, commit_id):
                flash('The document was saved.', 'ok')
                if redirect_url:
                    return redirect(redirect_url)
            else:
                flash('A conflict happened.', 'error')
        return render_template(
            template, cls=cls, part=part, version=version, **kwargs)

    @classmethod
    def view_edit(cls, part='index.rst.jinja2', version=None, **kwargs):
        """View the document edition form.

        :param part: part of the document to edit.
        :param version: version of the document to edit.

        """
        document = cls.from_data(version=version, **kwargs)
        template = document.environment.get_template(cls.edit_template)
        text = document.git.read(part).decode('utf-8')
        return jinja2.Markup(template.render(
            cls=cls, text=text, old_commit=document.git.commit.id, **kwargs))

    @classmethod
    def html(cls, template, part='index.rst.jinja2', version=None, **kwargs):
        """Render the HTML version of the document.

        :param template: application template including the render.
        :param part: part of the document to render.
        :param version: version of the document to render.

        """
        return render_template(template, cls=cls, version=version, **kwargs)

    @classmethod
    def view_html(cls, part='index.rst.jinja2', version=None, **kwargs):
        """View the HTML document ready to include in Jinja templates.

        :param part: part of the document to render.
        :param version: version of the document to render.

        """
        return jinja2.Markup(
            cls.generate_html(version=version, **kwargs)['html_body'])
