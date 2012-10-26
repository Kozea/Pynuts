"""Form validators for Pynuts."""
import os
from flask import current_app
from flask.ext.wtf import ValidationError, FileField
from flask.ext.uploads import UploadConfiguration




class AllowedFile(object):
    def __call__(self, form, field):

        field.upload_set._config = UploadConfiguration(destination=os.path.join(
            current_app.uploads_default_dest, field.name))
        if not field.has_file():
            raise ValidationError('FileField must not be empty.')
        field.upload_set.save(field.data)
