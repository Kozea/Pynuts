from flask import session, request, g
from application import app
from pynuts.rights import acl


class Context(app.Context):
    """This class create a context. You can add properties like and use methods
       in order to make rights. Your rights methods have to be decorated by
       `@acl` for access control in `allow_if` decorators. `allow_if` checks
       that the global context matches a criteria.

    """

    @property
    def person(self):
        """Returns the current logged on person, or None."""
        return session.get('id')

    @property
    def request_time(self):
        return g.context.get('_request_time')

    @request_time.setter
    def request_time(self, value):
        g.context['_request_time'] = value


@acl
def connected():
    """Returns whether the user is connected."""
    return g.context.person is not None


@acl
def connected_user():
    """Returns the connected user."""
    if g.context.person:
        return g.context.person == request.view_args.get('person_id')


@acl
def admin():
    """Returns whether the user is connected."""
    return session.get('login') == 'admin'


def dummy():
    return False
