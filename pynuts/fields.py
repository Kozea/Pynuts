"""Wtforms fields created for Pynuts."""

from wtforms import StringField
from wtforms.widgets import html_params, HTMLString
from flask.ext.wtf import FileField


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
    """Field handling file uploads."""
    def __init__(self, upload_set, *args, **kwargs):
        super(UploadField, self).__init__(*args, **kwargs)
        self.upload_set = upload_set


class ImageField(UploadField):
    """Field specifically handling image uploads."""
    def __init__(self, *args, **kwargs):
        super(ImageField, self).__init__(*args, **kwargs)
