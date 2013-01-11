# -*- coding: utf-8 -*-

"""Jinja environment filters for Pynuts."""

from flask import escape
from flask.ext.wtf import (
    QuerySelectField, QuerySelectMultipleField, BooleanField,
    DateField, DateTimeField)
from .fields import UploadField, ImageField


def data(field):
    """Field data beautifier.

    QuerySelectMultipleField
      Renders comma-separated data.
    QuerySelectField
      Renders the selected value.
    BooleanField
      Renders '✓' or '✕'
    DateField
      Renders the date
    ImageField
      Renders the image
    UploadField
      Renders a link to the uploaded file

    Example:

    .. sourcecode:: html+jinja

        <dd>{{ field | data }}</dd>

    """
    if isinstance(field, QuerySelectMultipleField):
        if field.data:
            return escape(
                u', '.join(field.get_label(data) for data in field.data))
        else:
            return u'∅'
    elif isinstance(field, QuerySelectField):
        if field.data:
            return escape(field.get_label(field.data))
    elif isinstance(field, BooleanField):
        return u'✓' if field.data else u'✕'
    elif isinstance(field, DateField) or isinstance(field, DateTimeField):
        if field.data:
            return field.data.strftime(field.format)
    elif isinstance(field, ImageField):
        if field.data:
            return '<img src="%s" alt="" />' % (field.upload_set.url(field.data))
    elif isinstance(field, UploadField):
        if field.data:
            return '<a href="%s">%s</a>' % (
                field.upload_set.url(field.data),
                field.data)
    return escape(field.data)
