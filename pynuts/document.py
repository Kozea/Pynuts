"""Document file for Pynuts."""

import os
import datetime
import docutils
import jinja2
import docutils.core
import mimetypes
from urllib import quote, unquote
from flask import (Response, render_template, request, redirect, flash,
                   url_for, jsonify)
from werkzeug.datastructures import Headers
from flask_weasyprint import HTML
from docutils_html5 import Writer

from .environment import create_environment
from .git import Git, ConflictError


class InvalidId(ValueError):
    """The '/' character is not allowed in document identifiers."""


class MetaDocument(type):
    """Metaclass for document classes."""
    def __init__(mcs, name, bases, dict_):
        if mcs.document_id_template:
            # TODO: find a better endpoint name than the name of the class
            if not mcs.type_name:
                mcs.type_name = mcs.__name__
            mcs._pynuts.documents[mcs.type_name] = mcs
            mcs._app.add_url_rule(
                '/_pynuts/resource/%s/<document_id>/'
                '<version>/<path:filename>' % (
                    mcs.type_name),
                endpoint='_pynuts-resource/' + mcs.type_name,
                view_func=mcs.static_route)
            mcs._app.add_url_rule(
                '/_pynuts/update_content', '_pynuts-update_content',
                mcs.update_content, methods=('POST',))
            if mcs.model_path and not os.path.isabs(mcs.model_path):
                mcs.model_path = os.path.join(
                    mcs._app.root_path, mcs.model_path)
            mcs.document_id_template = unicode(mcs.document_id_template)
            super(MetaDocument, mcs).__init__(name, bases, dict_)


class Document(object):
    """This class represents a document object.

    :param document_id: the id of the document
    :type document_id: str
    :param version: the SHA1 hash of the commit
    :type version: str

    """
    __metaclass__ = MetaDocument

    #: Jinja Environment
    jinja_environment = None

    #: Docutils settings
    docutils_settings = None

    #: Stylesheet name
    stylesheet = 'style.css'

    #: Template generating the document id
    document_id_template = None

    #: Name identifying the document type, default is the class name
    type_name = None

    #: Model path, absolute or relative to the application root path
    model_path = None

    # Templates
    edit_template = '_pynuts/edit_document.jinja2'

    def __init__(self, document_id, version=None):
        if '/' in repr(document_id):
            raise InvalidId("The '/' character is not allowed in "
                            "document identifiers.")
        self.document_id = document_id
        self.git = Git(
            self._pynuts.document_repository, branch=self.branch,
            commit=version)
        self.archive_git = Git(
            self._pynuts.document_repository, branch=self.archive_branch)

        loader = self.git.jinja_loader()
        self.jinja_environment = create_environment(loader)
        self.jinja_environment.globals['render_rest'] = \
            self._pynuts.render_rest
        # Take the class attribute
        docutils_settings = dict(self.docutils_settings or {})
        docutils_settings['_pynuts'] = self._pynuts
        # Set an attribute instance to mask the class instance
        self.docutils_settings = docutils_settings
        self.data = None

    @classmethod
    def list_document_ids(cls):
        """Return a list of document ids."""
        base = 'refs/heads/documents/' + quote(cls.type_name.encode('utf8'))
        for doc_id in cls._pynuts.document_repository.refs.keys(base=base):
            yield unquote(doc_id).decode('utf8')

    @classmethod
    def list_documents(cls):
        """Return the whole document list."""
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
        """Time of the document latest commit as an UTC naive datetime
        object.

        """
        return datetime.datetime.utcfromtimestamp(self.git.head.commit_time)

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

    def resource_url(self, filename):
        """Resource URL for the application."""
        return url_for(
            '_pynuts-resource/' + self.type_name,
            document_id=self.document_id,
            filename=filename,
            version=self.version)

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
    def generate_rest(cls, part='index.rst.jinja2', archive=False,
                      version=None, editable=True, **kwargs):
        """ Call the _generate_rest method to generate the ReStructuredText
            version of the given version of the document.
        """

        return cls.from_data(version=version, **kwargs)._generate_rest(
            part=part, archive=archive, editable=editable, **kwargs)

    def _generate_rest(self, part='index.rst.jinja2', archive=False,
                       editable=True, **kwargs):
        """Generate the ReStructuredText version of the document.

        :param part: part of the document to render
        :param archive: return archive content if `True`
        :param editable: if you use the 'Editable' pynuts'
            ReST directive and if you need to render html with 'contenteditable="false"',
            set this parameter to 'False'. For more info see :ref:`api`
        """
        part = 'index.rst' if archive else part
        if archive:
            return self.archive_git.read(part)
        else:
            template = self.jinja_environment.get_template(part)
            return template.render(resource=self.resource_url, document=self,
                                   editable=editable, **self.data)

    @classmethod
    def generate_html(cls, part='index.rst.jinja2', archive=False,
                      version=None, editable=True, **kwargs):
        """Generate the html document from a ReST file or a jinja2 template."""
        return cls.from_data(version=version, **kwargs)._generate_html(
            part=part, archive=archive, editable=editable)

    def _generate_html(self, part='index.rst.jinja2', archive=False,
                      editable=True):
        """Generate the HTML samples of the document.

        The output is a dict corresponding to the different HTML samples as
        generated by Docutils.

        :param part: part of the document to render
        :param archive: return archive content if `True`
        :param editable: if you use the 'Editable' pynuts'
            ReST directive and if you need to render html with 'contenteditable="false"',
            set this parameter to 'False'. For more info see :ref:`api`

        .. seealso::
           `Docutils writer publish parts
           <http://docutils.sourceforge.net/docs/api/publisher.html\
           #publish-parts-details>`_

        """
        part = 'index.rst' if archive else part
        source = self._generate_rest(
            part=part, archive=archive, editable=editable)

        settings = dict(self.docutils_settings)
        settings.setdefault('stylesheet', self.resource_url(self.stylesheet))
        parts = docutils.core.publish_parts(
            source=source, writer=Writer(),
            settings_overrides=settings)
        return parts

    @classmethod
    def generate_pdf(cls, part='index.rst.jinja2', version=None, archive=False,
                     **kwargs):
        """Generate the PDF document.

        :param part: part of the document to render.
        :param version: version of the document to render.
        :param version: whether to archive the given version of the document
        """
        return cls.from_data(version=version, **kwargs)._generate_pdf(
            part=part, archive=archive)

    def _generate_pdf(self, part='index.rst.jinja2', archive=False):
        """Generate the PDF version from the document.

        :param part: part of the document to render.
        :param archive: return archive content if `True`
        """

        part = 'index.rst' if archive else part
        html = self._generate_html(part=part, archive=archive)['whole']
        return HTML(string=html, encoding='utf8').write_pdf()

    @classmethod
    def download_pdf(cls, part='index.rst.jinja2', version=None, archive=False,
                     filename=None, **kwargs):
        """Get a HTTP response with PDF document as file in attachment.

        :param part: part of the document to render
        :param version: version of the document to render
        :param archive: whether to archive the given version of the document
        :param filename: attachment filename, expect unicode

        """
        part = 'index.rst' if archive else part
        headers = Headers()
        headers.add(
            'Content-Disposition', 'attachment',
            filename=(filename.encode('utf-8') if filename else None))
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
    def update_content(cls):
        """Update the ReST document.
        It is used by the javascript/AJAX save function.
        It gets the request as JSON and update all the parts of the document

        return document's information as JSON.

        'See the save function<>_' for more details.

        """

        contents = request.json['data']
        author_name = request.json['author']
        author_email = request.json['author_email']
        message = request.json['message']

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
            document.git.commit(
                author_name or 'Pynuts',
                author_email or 'pynut@pynuts.org',
                message or 'Edit %s' % document.document_id)
        return jsonify(documents=[{
            'document_type': document.type_name,
            'document_id': document.document_id,
            'version': document.version}
            for document in documents.values()])

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
        :param archive: return archive content if `True`
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
            template, document=cls, part=part, version=version,
            archive=archive, **kwargs)

    @classmethod
    def view_edit(cls, part='index.rst.jinja2', version=None, archive=False,
                  **kwargs):
        """View the document edition form.

        :param part: part of the document to edit
        :param version: version of the document to edit
        :param archive: return archive content if `True`

        """
        part = 'index.rst' if archive else part
        document = cls.from_data(version=version, **kwargs)
        template = document.jinja_environment.get_template(cls.edit_template)
        # TODO: what if archive==True?
        text = document.git.read(part).decode('utf-8')
        return jinja2.Markup(template.render(
            document=cls, text=text,
            old_commit=document.git.head.id, **kwargs))

    @classmethod
    def html(cls, template, part='index.rst.jinja2', version=None,
             archive=False, editable=True, **kwargs):
        """Render the HTML version of the document.

        :param template: application template including the render
        :param part: part of the document to render
        :param version: version of the document to render
        :param archive: return archive content if `True`
        :param editable: if you use the 'Editable' pynuts'
            ReST directive and if you need to render html with 'contenteditable="false"',
            set this parameter to 'False'. For more info see :ref:`api`

        """
        part = 'index.rst' if archive else part
        editable = False if archive else editable
        return render_template(
            template, document=cls, part=part, version=version,
            archive=archive, editable=editable, **kwargs)

    @classmethod
    def view_html(cls, part='index.rst.jinja2', version=None, archive=False,
                  html_part='article', editable=True, **kwargs):
        """View the HTML document ready to include in Jinja templates.

        :param part: part of the document to render
        :param version: version of the document to render
        :param archive: set it to 'True' if you render an archive
        :param html_part: the docutils publish part to render
        :param editable: if you use the 'Editable' pynuts'
            ReST directive and if you need to render html with 'contenteditable="false"',
            set this parameter to 'False'. For more info see :ref:`api`

        """
        part = 'index.rst' if archive else part
        editable = False if archive else editable
        return jinja2.Markup(
            cls.generate_html(
                part=part, version=version, archive=archive, editable=editable,
                **kwargs)[html_part].decode('utf-8'))

    def get_content(self, part):
        """ Return an object alllowing IO operations on any content of the part
            in its git repository.
        """
        return Content(self.git, part)


class Content(object):
    """The content class.
    It allows you to read/write any content in a git repository.

    :param git: The git repository
    :type git: Git object

    :param part: The file in the repository
    :type part: str

    """
    def __init__(self, git, part):
        self.git = git
        self.part = part

    def read(self):
        """Read part's content."""
        return self.git.read(self.part)

    def write(self, content, author_name=None, author_email=None,
              message=None):
        """Write content in part.

        :param content: the content to store
        :param author_name: the commit author name
        :param author_email: the commit author email
        :param message: the commit message

        """
        try:
            self.git.write(self.part, content)
            self.git.commit(
                author_name or 'Pynuts',
                author_email or 'pynut@pynuts.org',
                message or 'Edit %s' % self.part)
        except ConflictError:
            raise ConflictError
        else:
            return True
