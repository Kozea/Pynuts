"""Wtforms fields created for Pynuts."""

from wtforms import StringField
from wtforms.widgets import html_params, HTMLString
from flask.ext.uploads import UploadSet
from flask.ext.wtf import FileField
from flask import current_app


class Editable(object):
    """Contenteditable widget."""
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        return HTMLString(
            u'<div contenteditable="true" %s>%s</div>' %
            (html_params(name=field.name, **kwargs),
             unicode(field._value())))


class EditableField(StringField):
    """Contenteditable field."""
    widget = Editable()


class UploadField(FileField):
    """Field handling the file upload operation and validation."""
    def __init__(self, upload_set, *args, **kwargs):
        super(UploadField, self).__init__(*args, **kwargs)
        label, extensions = upload_set
        self.upload_set = UploadSet(name=label,
                                    extensions=extensions,
                                    default_dest=lambda app: current_app.uploads_default_dest)
