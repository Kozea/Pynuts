"""Form validators for Pynuts."""

from flask.ext.wtf import ValidationError


class AllowedFile(object):
    """ Check if uploaded file can be saved, according to the rules
    defined by the corresponding UploadSet.

    If the file breaks the UploadSet rule, raise a ``ValidationError``.

    :raises: ValidationError
    """

    def __call__(self, form, field):
        if not field.has_file():
            return
        if not field.upload_set.file_allowed(
                field.data, field.data.filename.lower()):
            extension = field.data.filename.split('.')[-1]
            field_label = field.label.text
            raise ValidationError('The %s field does not allow the upload of '
                '%s files' % (field_label, extension))


class MaxSize(object):
    """ A validator ensuring that uploaded file size is under the allowed size.
    If its size exceeds the maximum size, raises a ``ValidationError``.

    :param size: The maximum size to accept, in MB. The default value is 5MB.
    :type size: float, int

    :raises: ValidationError
    """
    def __init__(self, size=5):
        self.max_size = size

    def __call__(self, form, field):
        """Check if uploaded file is under specified max size."""
        if not field.has_file():
            return
        if self.byte_size < self.stream_size(field.data.stream):
            raise ValidationError('Maximum authorized file size is %.1f MB' % (
                self.max_size))

    @property
    def byte_size(self):
        """Returns the value of the max_size attribute, in bytes."""
        return self.max_size * 1048576

    @staticmethod
    def stream_size(stream):
        """Returns the size (in bytes) of a byte stream.

        :seealso: https://groups.google.com/forum/?fromgroups=#!searchin/pocoo-libs/FileStorage/pocoo-libs/n9S53qFqlwo/zwYiBcDwP8gJ
        """
        if hasattr(stream, "getvalue"):
            file_size = len(stream.getvalue())
        else:
            stream.seek(0, 2)
            file_size = stream.tell()
            stream.seek(0)
        return file_size
