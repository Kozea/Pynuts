"""Directives for Pynuts documents."""

import json

from docutils.parsers.rst import directives, Directive
import docutils.core

from .git import NotFoundError


class _Tag(Directive):
    """ReST abstact directive used for Editable and Content."""
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True

    def run(self):
        document_type, document_id, version, part = \
            self.arguments[0].split('/')
        cls = self.state.document.settings._pynuts.documents[document_type]
        self.document = cls(document_id, version)
        self.attributes = {
            'data-document-version': version,
            'data-part': part,
            'data-document-type': document_type,
            'data-document-id': document_id
        }
        self.attributes.update({
            key: ' '.join(values) for key, values in self.options.items()})
        self.attributes = {
            key: value for key, value in self.attributes.items() if value}
        self.content = self.document.git.read(part).decode('utf-8')


class Editable(_Tag):
    """ReST directive creating an HTML contenteditable tag.

    The directive's argument must look like this:
    `document_type/document_id/version/part`

    You can put those optional attributes on your editable content:

    - `title`
    - `id`
    - `class`

    """
    option_spec = {
        'title': directives.unchanged,
        'class': directives.class_option,
        'id': directives.class_option,
        'contenteditable': directives.class_option,
    }

    def run(self):
        try:
            super(Editable, self).run()
        except NotFoundError:
            self.parsed_content = docutils.core.publish_parts(
                '\n'.join(self.content), writer_name='html')['body']
        content = '<div %s>%s</div>' % (
            ' '.join(('%s="%s"' % a) for a in self.attributes.items()),
            self.parsed_content or '')
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('editable', Editable)


class Content(_Tag):
    """ReST directive creating an editable div with specific content.

    Use this directive if you have specific content you want to render which is
    not possible with the ReST syntax.

    The content data has to look like a list interpretable as JSON
    (e.g. `["Product", "Quantity", "Price"]`).

    You have to specify the renderer in the directive's attribute. It's will be
    associated with the function in your document class that renders the
    content.

    For example, the Content directive can be used for rendering a table with
    some contenteditable columns::

      from myapplication import app
      class MyDocument(app.Document):
          def render_table(self, data):
              template = self.jinja_environment.get_template('price.jinja2')
              return template.render(data=data)

    Then you have to create the jinja2 template and use data as a list.

    The directive's argument must look like this:
    `document_type/document_id/version/part`

    Optional attributes:

    - `title`
    - `id`
    - `renderer`: document's callback method rendering the data

    """
    option_spec = {
        'class': directives.class_option,
        'id': directives.class_option,
        'renderer': directives.unchanged,
    }

    def run(self):
        try:
            super(Content, self).run()
        except NotFoundError:
            self.parsed_content = '\n'.join(self.content)
        render = getattr(
            self.document, 'render_%s' % self.options.pop('renderer'))
        self.attributes.pop('renderer', None)
        content = '<div data-content="true" %s>%s</div>' % (
            ' '.join(('%s="%s"' % a) for a in self.attributes.items()),
            render(json.loads(self.parsed_content)) or '')
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('content', Content)
