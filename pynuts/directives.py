from docutils.parsers.rst import directives, Directive
import docutils.core

from pynuts.git import NotFoundError


class Editable(Directive):
    """A rest directive which creates a contenteditable in HTML.

    The directive's argument must looks like this:
    `document_type/document_id/version/part`

    """
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {'title': directives.class_option,
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
            attr[k] = ' '.join(self.options.get(k, []))

        content = '<div %s >%s</div>' % (
                ' '.join(('%s="%s"' % (k, v)) for k, v in attr.items() if v),
                content or '')
        return [docutils.nodes.raw('', content, format='html')]

directives.register_directive('editable', Editable)
