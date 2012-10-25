"""Directives for Pynuts documents."""

import json

from docutils.parsers.rst import directives, Directive
import docutils.core

from .git import NotFoundError


class Editable(Directive):
    """A rest directive which creates a contenteditable in HTML.

    The directive's argument must look like this:
    `document_type/document_id/version/part`

    You can put those optional attributes on your editable content :
      - `title`
      - `id`
      - `class`
      - `contenteditable`

    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {'title': directives.unchanged,
                   'class': directives.class_option,
                   'id': directives.class_option,
                   'contenteditable': directives.class_option}

    def run(self):
        document_type, document_id, version, part = \
            self.arguments[0].split('/')
        cls = self.state.document.settings._pynuts.documents[document_type]
        document = cls(document_id, version)
        try:
            content = document.git.read(part).decode('utf-8')
        except NotFoundError:
            content = '\n'.join(self.content)
            content = docutils.core.publish_parts(
                content, writer_name='html')['body']

        attr = {'contenteditable': 'true',
                'data-document-version': version,
                'data-part': part,
                'data-document-type': document_type,
                'data-document-id': document_id}

        for k in self.option_spec.keys():
            if k == 'title':
                attr[k] = self.options.get(k)
            elif k == 'contenteditable':
                attr[k] = ' '.join(self.options.get(k, ['true']))
            else:
                attr[k] = ' '.join(self.options.get(k, []))
        content = '<div %s>%s</div>' % (
                ' '.join(('%s="%s"' % (k, v)) for k, v in attr.items() if v),
                content or '')
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('editable', Editable)


class Content(Directive):
    """A rest directive which create an editable div with specific content.

    Use this directive if you have specific content you want to render which is not possible with the ReST synthax.
    The content data has to look like a list interpretable as JSON (e.g. `["Product", "Quantity", "Price"]`).
    You have to specify the renderer in the directive's attribute. It's will be associated with the function in your document class that renders the content.
    For example, the Content directive can be used for rendering a table with some contenteditable columns::

      from myapplication import app
      class MyDocument(app.Document):
          def render_table(self, data):
              template = self.jinja_environment.get_template('price.jinja2')
              return template.render(data=data)

    Then you have to create the jinja2 template and use data as a list.

    The directive's argument must look like this:
    `document_type/document_id/version/part`

    Optional attributes :
      - `title`
      - `id`
      - `renderer` : Call a function in your directive.

    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {'class': directives.class_option,
                   'id': directives.class_option,
                   'renderer': directives.unchanged}

    def run(self):
        document_type, document_id, version, part = \
            self.arguments[0].split('/')
        cls = self.state.document.settings._pynuts.documents[document_type]
        document = cls(document_id, version)
        try:
            content = document.git.read(part).decode('utf-8')
        except NotFoundError:
            content = '\n'.join(self.content)

        data = json.loads(content)
        render = getattr(document, 'render_%s' % self.options.pop('renderer'))

        attr = {'data-document-version': version,
                'data-part': part,
                'data-document-type': document_type,
                'data-document-id': document_id,
                'data-content': 'true'}
        attr.update(dict(
            (key, ' '.join(values)) for key, values in self.options.items()))

        content = '<div %s>%s</div>' % (
                ' '.join(('%s="%s"' % (k, v)) for k, v in attr.items() if v),
                render(data) or '')
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('content', Content)
