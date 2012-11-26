"""Rights for Pynuts."""

from flask import abort, request
from functools import wraps


class MetaContext(type):
    """Get context object for rights."""
    def __init__(cls, name, bases, dict_):
        cls._pynuts._context_class = cls


# These classes are decorators, they can begin with an lowercase letter
class acl(object):  # pylint: disable=C0103
    """Utility decorator for access control in ``allow_if`` decorators.

    Allows to write:
    ``@allow_if((Is.admin | Is.in_domain) & ~Is.in_super_domain)``
    given that Is module functions are decorated by acl

    It implements the following operators:

    * ``a & b``: a and b
    * ``a | b``: a or  b
    * ``a ^ b``: a xor b
    * ``~ a``: not a

    """
    def __init__(self, function=lambda context: True):
        self.__name__ = function.__name__
        self.function = function

    def __call__(self, **kwargs):
        """Call the ACL function."""
        return self.function(**(kwargs or request.view_args or {}))

    def __or__(self, other):
        """Or operator."""
        def result(**kwargs):
            """Closure for the or operator."""
            return self(**kwargs) or other(**kwargs)
        result.__name__ = '%s | %s' % (self.__name__, other.__name__)
        return acl(result)

    def __ror__(self, other):
        """Right or operator."""
        def result(**kwargs):
            """Closure for the right or operator."""
            return other(**kwargs) or self(**kwargs)
        result.__name__ = '%s | %s' % (other.__name__, self.__name__)
        return acl(result)

    def __and__(self, other):
        """And operator."""
        def result(**kwargs):
            """Closure for the and operator."""
            return self(**kwargs) and other(**kwargs)
        result.__name__ = '%s & %s' % (self.__name__, other.__name__)
        return acl(result)

    def __rand__(self, other):
        """Right and operator."""
        def result(**kwargs):
            """Closure for the right and operator."""
            return other(**kwargs) and self(**kwargs)
        result.__name__ = '%s & %s' % (other.__name__, self.__name__)
        return acl(result)

    def __xor__(self, other):
        """Exclusive or operator."""
        def result(**kwargs):
            """Closure for the exclusive or operator."""
            return (
                self(**kwargs) and not other(**kwargs) or
                other(**kwargs) and not self(**kwargs))
        result.__name__ = '%s ^ %s' % (self.__name__, other.__name__)
        return acl(result)

    def __rxor__(self, other):
        """Right exclusive or operator."""
        def result(**kwargs):
            """Closure for the right exclusive or operator."""
            return (
                other(**kwargs) and not self(**kwargs) or
                self(**kwargs) and not other(**kwargs))
        result.__name__ = '%s ^ %s' % (other.__name__, self.__name__)
        return acl(result)

    def __invert__(self):
        """Invert operator."""
        def result(**kwargs):
            """Closure for the invert operator."""
            return not self(**kwargs)
        result.__name__ = '~%s' % self.__name__
        return acl(result)


class allow_if(object):  # pylint: disable=C0103
    """Check that the global context matches a criteria."""
    def __init__(self, auth_fun, exception=None):
        self.auth_fun = auth_fun
        self.exception = exception

    def __call__(self, function):
        """Check the global context."""
        @wraps(function)
        def check_auth(*args, **kwargs):
            """Function wrapper."""
            if self.auth_fun():
                return function(*args, **kwargs)
            else:
                if self.exception:
                    raise self.exception
                else:
                    abort(403)

        check_auth._auth_fun = self.auth_fun
        return check_auth
