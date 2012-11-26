"""Jinja2 environment for pynuts."""

# Set the jinja2 environment by defining templates location and globals.
import flask
from jinja2 import nodes, Environment, PackageLoader, ChoiceLoader
from jinja2.ext import Extension

from . import filters


class ShowOnMatch(Extension):
    """This extension introduces a new tag ``showonmatch``, allowing\
    conditional output of a its body according to a css selector.

    This will output an ul with lis if mylist is not empty.

    .. sourcecode:: html+jinja

        {% showonmatch 'ul li' %}
          <ul>
          {% for a in mylist %}
            <li>{{a}}</li>
          {% endfor %}
          </ul>
        {% endshowonmatch %}

    """
    tags = set(['showonmatch'])

    def parse(self, parser):
        # Parse the current block
        lineno = parser.stream.next().lineno
        selector = parser.parse_expression()
        body = parser.parse_statements(('name:else', 'name:endshowonmatch'))
        token = next(parser.stream)
        if token.test('name:else'):
            else_ = parser.parse_statements(
                ('name:endshowonmatch',), drop_needle=True)
        else:
            else_ = None

        # Create an (anonymous) macro containing the block
        macro_name = parser.free_identifier()
        body_expr = nodes.Macro(macro_name.name, [], [], body)
        name = parser.free_identifier()

        # Call the macro, and store the result in an anonymous variable
        # Equivalent to freevar = macro()
        assign_node = nodes.Assign(name, nodes.Call(nodes.Name(macro_name.name,
            'load'), [], [],
                None, None))
        assign_node = assign_node.set_lineno(lineno)

        # Importe the needed lxml libraries
        import_node = nodes.ImportedName('lxml.html.fromstring')
        cssselector_node = nodes.ImportedName('lxml.cssselect.CSSSelector')

        # Creates the if's test node
        # Jinja AST equivalent of CSSSelector(selector)(fromstring(freevar))
        test_node = nodes.Call(nodes.Call(cssselector_node,
            [selector], [], None, None), [nodes.Call(import_node,
                [name],
                [], None, None)], [], None, None)

        # Fill the if node
        if_node = nodes.If()
        if_node.test = test_node
        if_node.body = [nodes.Output([name])]
        if_node.else_ = else_
        if_node = if_node.set_lineno(lineno)

        # Returns an ast containing:
        # the macro definition, a call to this macro assigned to a variable,
        # and a test on the the selectors
        return [body_expr, assign_node, if_node]


def create_environment(loader):
    """Create a new Jinja2 environment with Pynuts helpers."""
    loaders = (loader, PackageLoader('pynuts', 'templates'))
    environment = Environment(
        loader=ChoiceLoader(loaders), extensions=[ShowOnMatch])
    environment.globals.update({'url_for': flask.url_for})
    environment.filters['data'] = filters.data
    return environment


def alter_environment(environment):
    """Create a new Jinja2 environment with Pynuts helpers."""
    environment.loader = ChoiceLoader(
        (environment.loader, PackageLoader('pynuts', 'templates')))
    environment.add_extension(ShowOnMatch)
    environment.filters['data'] = filters.data
