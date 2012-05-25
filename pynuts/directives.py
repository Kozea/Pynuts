import json

from docutils.parsers.rst import directives, Directive
import docutils.core

from pynuts.git import NotFoundError


class Editable(Directive):
    """A rest directive which creates a contenteditable in HTML.

    The directive's argument must look like this:
    `document_type/document_id/version/part`

    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {'title': directives.unchanged,
                   'class': directives.class_option,
                   'id': directives.class_option}

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
            else:
                attr[k] = ' '.join(self.options.get(k, []))

        content = '<div %s>%s</div>' % (
                ' '.join(('%s="%s"' % (k, v)) for k, v in attr.items() if v),
                content or '')
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('editable', Editable)


class Content(Directive):
    """A rest directive...

    The directive's argument must look like this:
    `document_type/document_id/version/part`

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
        attr.update({
            key: ' '.join(values) for key, values in self.options.items()})

        content = '<div %s>%s</div>' % (
                ' '.join(('%s="%s"' % (k, v)) for k, v in attr.items() if v),
                render(data) or '')
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('content', Content)
