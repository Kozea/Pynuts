"""Document file for Pynuts."""

import os
import datetime
import docutils
import jinja2
import docutils.core
import mimetypes
from urllib import quote, unquote
from flask import (Response, render_template, request, redirect, flash,
                   url_for)
from werkzeug.datastructures import Headers
from jinja2 import ChoiceLoader
from weasyprint import HTML
from docutils_html5 import Writer

from .environment import create_environment
from .git import Git, ConflictError


class MetaDocument(type):
    """Metaclass for document classes."""
    def __init__(cls, name, bases, dict_):
        if cls.document_id_template:
            # TODO: find a better endpoint name than the name of the class
            if not cls.type_name:
                cls.type_name = cls.__name__
            cls._pynuts.documents[cls.type_name] = cls
            cls._pynuts.add_url_rule(
                '/_resource/%s/<document_id>/<version>/<path:filename>' % (
                    cls.type_name),
                endpoint='_pynuts-resource/' + cls.type_name,
                view_func=cls.static_route)
            if cls.model_path and not os.path.isabs(cls.model_path):
                cls.model_path = os.path.join(
                    cls._pynuts.root_path, cls.model_path)
            cls.document_id_template = unicode(cls.document_id_template)
            super(MetaDocument, cls).__init__(name, bases, dict_)


class Document(object):
    """This class represents a document object. """
    __metaclass__ = MetaDocument

    #: Jinja Environment
    jinja_environment = None

    #: Docutils settings
    docutils_settings = None

    #: Template generating the document id
    document_id_template = None

    #: Name identifying the document type, default is the class name
    type_name = None

    #: Model path, absolute or relative to the application root path
    model_path = None

    # Templates
    edit_template = 'edit_document.jinja2'

    def __init__(self, document_id, version=None):
        self.document_id = document_id
        self.git = Git(
            self._pynuts.document_repository, branch=self.branch,
            commit=version)
        self.archive_git = Git(
            self._pynuts.document_repository, branch=self.archive_branch)

        self.jinja_environment = create_environment()
        self.jinja_environment.loader = ChoiceLoader((
            self.git.jinja_loader(), self.jinja_environment.loader))
        self.jinja_environment.globals['render_rest'] = \
            self._pynuts.render_rest
        # Take the class attribute
        docutils_settings = dict(self.docutils_settings or {})
        docutils_settings['_pynuts'] = self._pynuts
        if self.git.head:
            docutils_settings.setdefault(
                'stylesheet', self.resource_url('style.css', external=True))
        # Set an attribute instance to mask the class instance
        self.docutils_settings = docutils_settings
        self.data = None

    @classmethod
    def list_document_ids(cls):
        base = 'refs/heads/documents/' + quote(cls.type_name.encode('utf8'))
        for doc_id in cls._pynuts.document_repository.refs.keys(base=base):
            yield unquote(doc_id).decode('utf8')

    @classmethod
    def list_documents(cls):
        return (cls(doc_id) for doc_id in cls.list_document_ids())

    @property
    def branch(self):
        """Branch name of the document."""
        return quote((
            'documents/%s/%s' % (self.type_name, self.document_id)
        ).encode('utf8'))

    @property
    def archive_branch(self):
        """Branch name of the document archives."""
        return quote((
            'archives/%s/%s' % (self.type_name, self.document_id)
        ).encode('utf8'))

    @property
    def version(self):
        """Actual git version of the document."""
        return self.git.head.id

    @property
    def datetime(self):
        """Datetime of the document latest commit."""
        return datetime.datetime.fromtimestamp(self.git.head.commit_time)

    @property
    def author(self):
        """Author of the document latest commit."""
        return self.git.head.author.decode('utf-8')

    @property
    def message(self):
        """Message of the document latest commit."""
        return self.git.head.message.decode('utf-8')

    @property
    def history(self):
        """Yield the parent documents."""
        git = Git(self._pynuts.document_repository, branch=self.branch)
        for version in git.history():
            yield type(self)(self.document_id, version=version)

    @property
    def archive_history(self):
        """Yield the parent documents stored as archives."""
        for version in self.archive_git.history():
            yield type(self)(self.document_id, version=version)

    @classmethod
    def from_data(cls, version=None, **kwargs):
        """Create an instance of the class from the given data."""
        doc_id = cls.document_id_template.format(**kwargs)
        instance = cls(doc_id, version=version)
        instance.data = kwargs
        return instance

    def resource_base64(self, filename, **kwargs):
        """Resource content encoded in base64."""
        mimetype, _ = mimetypes.guess_type(filename)
        return 'data:%s;base64,%s' % (
            mimetype or '',
            self.git.read(filename).encode('base64').replace('\n', ''))

    def resource_url(self, filename, external=False):
        """Resource URL for the application."""
        return url_for(
            '_pynuts-resource/' + self.type_name,
            document_id=self.document_id,
            filename=filename,
            version=self.version,
            _external=external)

    @classmethod
    def static_route(cls, document_id, filename, version):
        """Serve static files for documents.

        :param document_id: id of the document
        :param filename: name of the document
        :param version: version of the document

        """
        mimetype, _ = mimetypes.guess_type(filename)
        return Response(
            cls(document_id, version).git.read(filename), mimetype=mimetype)

    @classmethod
    def generate_rest(cls, part='index.rst.jinja2', resource_type='url',
                      archive=False, version=None, **kwargs):
        return cls.from_data(version=version, **kwargs)._generate_rest(
            part='index.rst.jinja2', resource_type='url', archive=False)

    def _generate_rest(self, part='index.rst.jinja2', resource_type='url',
                      archive=False):
        """Generate the ReStructuredText version of the document.

        :param part: part of the document to render
        :param resource_type: external resource type: `url` or `base64`
        :param version: version of the document to render
        :param archive: return archive content if `True`

        """
        part = 'index.rst' if archive else part
        if archive:
            return self.git.read(part)
        else:
            template = self.jinja_environment.get_template(part)
            resource = getattr(self, 'resource_%s' % resource_type)
            return template.render(
                resource=resource, document=self, **self.data)

    @classmethod
    def generate_html(cls, part='index.rst.jinja2', resource_type='url',
                      archive=False, version=None, **kwargs):
        return cls.from_data(version=version, **kwargs)._generate_html(
            part='index.rst.jinja2', resource_type='url', archive=False)

    def _generate_html(self, part='index.rst.jinja2', resource_type='url',
                      archive=False):
        """Generate the HTML samples of the document.

        The output is a dict corresponding to the different HTML samples as
        generated by Docutils.

        :param part: part of the document to render
        :param resource_type: external resource type: 'url' or 'base64'
        :param version: version of the document to render


        .. seealso::
           `Docutils writer publish parts
           <http://docutils.sourceforge.net/docs/api/publisher.html\
           #publish-parts-details>`_

        """
        part = 'index.rst' if archive else part
        source = self._generate_rest(
            part=part, archive=archive, resource_type=resource_type)
        parts = docutils.core.publish_parts(
            source=source, writer=Writer(),
            settings_overrides=self.docutils_settings)
        return parts

    @classmethod
    def generate_pdf(cls, part='index.rst.jinja2', version=None, archive=False,
                     **kwargs):
        """Generate the PDF version from the document.

        :param part: part of the document to render.
        :param version: version of the document to render.

        """

        part = 'index.rst' if archive else part
        html = cls.generate_html(
            part=part, resource_type='base64', archive=archive,
            version=version, **kwargs)['whole']
        # TODO: stylesheets
        return HTML(string=html.encode('utf-8')).write_pdf()

    @classmethod
    def download_pdf(cls, part='index.rst.jinja2', version=None, archive=False,
                     filename=None, **kwargs):
        """Get a HTTP response with PDF document as file in attachment.

        :param part: part of the document to render
        :param version: version of the document to render
        :param filename: attachment filename

        """
        part = 'index.rst' if archive else part
        headers = Headers()
        headers.add('Content-Disposition', 'attachment', filename=filename)
        pdf = cls.generate_pdf(
            part=part, version=version, archive=archive, **kwargs)
        return Response(pdf, mimetype='application/pdf', headers=headers)

    @classmethod
    def archive(cls, part='index.rst.jinja2', version=None,
                author_name=None, author_email=None, message=None, **kwargs):
        """Archive the given version of the document.

        :param part: part of the document to archive
        :param version: version of the document to archive
        :param author_name: commit author name
        :param author_email: commit author email
        :param message: commit message

        """
        document = cls.from_data(version=version, **kwargs)
        document.git.write(
            os.path.splitext(part)[0],
            document.generate_rest(part=part, **kwargs).encode('utf-8'))
        git = document.archive_git
        git.tree = document.git.tree
        git.commit(
            author_name or 'Pynuts',
            author_email or 'pynut@pynuts.org',
            message or 'Archive %s' % document.document_id)

    @classmethod
    def update_content(cls, contents, author_name=None, author_email=None,
                       message=None):
        """Update the ReST document.

        :param contents: This must contain the type of the document you want
                         to edit, the id of the document, the version and
                         the part wich will be updated.
        :type contents: Dict
        :param author_name: commit author name
        :param author_email: commit author email
        :param message: commit message

        """
        documents = {}
        for values in contents:
            key = (values['document_type'], values['document_id'])
            if key in documents:
                document = documents[key]
            else:
                cls = cls._pynuts.documents[values['document_type']]
                document = cls(values['document_id'], values['version'])
                documents[key] = document
            document.git.write(values['part'],
                               values['content'].encode('utf-8'))
        for document in documents.values():
            try:
                document.git.commit(
                    'Pynuts',
                    'pynuts@pynuts.org',
                    'Edit %s' % document.document_id)
            except ConflictError:
                return False
        return [{
            'document_type': document.type_name,
            'document_id': document.document_id,
            'version': document.version}
            for document in documents.values()]

    @classmethod
    def create(cls, author_name=None, author_email=None, message=None,
               **kwargs):
        """Create the ReST document.

        Return `True` if the document has been created, `False` if the
        document id was already used.

        :param author_name: commit author name
        :param author_email: commit author email
        :param message: commit message

        """
        document = cls.from_data(**kwargs)
        git = document.git
        git.tree = git.store_directory(cls.model_path)
        git.commit(
            author_name or 'Pynuts',
            author_email or 'pynut@pynuts.org',
            message or 'Create %s' % document.document_id)

    @classmethod
    def edit(cls, template, part='index.rst.jinja2', version=None,
             author_name=None, author_email=None, message=None, archive=False,
             redirect_url=None, **kwargs):
        """Edit the document.

        :param template: application template with edition form
        :param part: part of the document to edit
        :param version: version of the document to edit
        :param author_name: commit author name
        :param author_email: commit author email
        :param message: commit message
        :param redirect_url: route to go after saving

        Return ``True`` if the document has been edited, ``False`` if the
        document id was already used.

        """
        if request.method == 'POST':
            document = cls.from_data(
                version=request.form['_old_commit'], **kwargs)
            git = document.archive_git if archive else document.git
            git.write(
                'index.rst' if archive else part,
                request.form['document'].encode('utf-8'))
            try:
                git.commit(
                    author_name or 'Pynuts',
                    author_email or 'pynut@pynuts.org',
                    message or 'Edit %s' % document.document_id)
            except ConflictError:
                flash('A conflict happened.', 'error')
            else:
                flash('The document was saved.', 'ok')
                if redirect_url:
                    return redirect(redirect_url)

        return render_template(
            template, cls=cls, part=part, version=version, archive=archive,
            **kwargs)

    @classmethod
    def view_edit(cls, part='index.rst.jinja2', version=None, archive=False,
                  **kwargs):
        """View the document edition form.

        :param part: part of the document to edit
        :param version: version of the document to edit

        """
        part = 'index.rst' if archive else part
        document = cls.from_data(version=version, **kwargs)
        template = document.jinja_environment.get_template(cls.edit_template)
        # TODO: what if archive==True?
        text = document.git.read(part).decode('utf-8')
        return jinja2.Markup(template.render(
            cls=cls, text=text, old_commit=document.git.head.id, **kwargs))

    @classmethod
    def html(cls, template, part='index.rst.jinja2', version=None,
             archive=False, **kwargs):
        """Render the HTML version of the document.

        :param template: application template including the render
        :param part: part of the document to render
        :param version: version of the document to render

        """
        part = 'index.rst' if archive else part
        return render_template(
            template, cls=cls, part=part, version=version, archive=archive,
            **kwargs)

    @classmethod
    def view_html(cls, part='index.rst.jinja2', version=None, archive=False,
                  html_part='article', **kwargs):
        """View the HTML document ready to include in Jinja templates.

        :param part: part of the document to render
        :param version: version of the document to render

        """
        part = 'index.rst' if archive else part
        return jinja2.Markup(
            cls.generate_html(
                part=part, version=version, archive=archive,
                **kwargs)[html_part].decode('utf-8'))
