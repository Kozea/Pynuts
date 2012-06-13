"""Jinja environment filters for Pynuts."""

from flask import escape
from flask.ext.wtf import QuerySelectField, QuerySelectMultipleField


def data(field):
    """Return data according to a specific field."""
    if isinstance(field, QuerySelectMultipleField):
        if field.data:
            return escape(
                u', '.join(field.get_label(data) for data in field.data))
    elif isinstance(field, QuerySelectField):
        if field.data:
            return escape(field.get_label(field.data))
    return escape(field.data)
