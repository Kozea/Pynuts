import os
import errno
import functools
from io import BytesIO

from dulwich.repo import Repo
from flask import safe_join
from werkzeug.exceptions import NotFound as werkzeug_NotFound
from jinja2 import BaseLoader, TemplateNotFound


class FileNotFound(IOError):
    """No such file or directory."""


class NotAFile(IOError):
    """open() on a directory or other non-file object."""

class NotADirectory(IOError):
    """listdir() on a file or other non-directory object."""


def convert_errors(function):
    @functools.wraps(function)
    def wrapper(self, path):
        try:
            return function(self, path)
        except (OSError, IOError) as exc:
            if exc.errno == errno.ENOENT:  # No such file or directory
                raise FileNotFound(path)
            elif exc.errno == errno.EISDIR:  # Is a directory
                raise NotAFile(path)
            elif exc.errno == errno.ENOTDIR:  # Not a directory
                raise NotADirectory(path)
            else:
                raise
        except werkzeug_NotFound:
            raise FileNotFound(path)
    return wrapper


class RealFS(object):
    def __init__(self, root):
        self.root = root

    def _absolute_path(self, path):
        if path.startswith('/'):
            path = path[1:]
        return safe_join(self.root, path)

    @convert_errors
    def filename(self, path):
        return self._absolute_path(path)

    @convert_errors
    def listdir(self, path):
        return os.listdir(self._absolute_path(path))

    @convert_errors
    def open(self, path):
        # Read-only
        return open(self._absolute_path(path), 'rb')

    @convert_errors
    def getmtime(self, path):
        return os.path.getmtime(self._absolute_path(path))

    @convert_errors
    def isdir(self, path):
        return os.path.isdir(self._absolute_path(path))

    @convert_errors
    def isfile(self, path):
        return os.path.isfile(self._absolute_path(path))


class GitFS(object):
    def __init__(self, repository, commit_sha):
        self.repository = Repo(repository)
        self.commit = self.repository.commit(commit_sha)
        self.tree = self.repository.tree(self.commit.tree)

    def filename(self, path):
        return '<commit %s>/%s' % (self.commit.id, path)

    def _lookup(self, path):
        parts = [part for part in path.split('/') if part]
        tree = self.tree
        if not parts:
            return tree
        get_tree = self.repository.tree
        for i, part in enumerate(parts):
            if i:
                tree = get_tree(sha)
            try:
                mode, sha = tree[part]
            except KeyError:
                raise FileNotFound(path)
        return self.repository.get_object(sha)

    def listdir(self, path):
        tree = self._lookup(path)
        if tree.type_name != 'tree':
            raise NotADirectory(path)
        return list(tree)

    def open(self, path):
        blob = self._lookup(path)
        if blob.type_name != 'blob':
            raise NotAFile(path)
        # TODO: find a way to make a file-like without reading everything
        # in memory?
        return BytesIO(blob.data)

    def isdir(self, path):
        try:
            return self._lookup(path).type_name == 'tree'
        except FileNotFound:
            return False

    def isfile(self, path):
        try:
            return self._lookup(path).type_name == 'blob'
        except FileNotFound:
            return False

    def getmtime(self, path):
        self._lookup(path)  # raise if not found
        return self.commit.commit_time


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
