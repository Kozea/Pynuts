"""Helpers for Pynuts."""

def with_metaclass(meta, *bases):
    """Create a base class with a metaclass.

    Stolen from six.

    """
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})
