import os

from flask import safe_join
from werkzeug.exceptions import NotFound
from jinja2 import BaseLoader, TemplateNotFound


class RealFS(object):
    def __init__(self, root):
        self.root = root

    def _absolute_path(self, path):
        if path.startswith('/'):
            path = path[1:]
        try:
            return safe_join(self.root, path)
        except NotFound:
            raise OSError('No such file or directory')

    def filename(self, path):
        return self._absolute_path(path)

    def listdir(self, path):
        return os.listdir(self._absolute_path(path))

    def open(self, path):
        # Read-only
        return open(self._absolute_path(path), 'rb')

    def isdir(self, path):
        return os.path.isdir(self._absolute_path(path))

    def isfile(self, path):
        return os.path.isfile(self._absolute_path(path))

    def getmtime(self, path):
        return os.path.getmtime(self._absolute_path(path))


class JinjaAbstractFSLoader(BaseLoader):
    def __init__(self, fs):
        self.fs = fs

    def get_source(self, environment, template):
        if not self.fs.isfile(template):
            raise TemplateNotFound(template)
        mtime = self.fs.getmtime(template)
        with self.fs.open(template) as fd:
            source = fd.read().decode('utf-8')
        # filename might be None
        return source, self.fs.filename(template), lambda: \
            self.fs.getmtime(template) == mtime
