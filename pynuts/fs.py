import os
import time
import errno
import functools

from dulwich.repo import Repo, Blob, Tree, Commit
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


class GitFS(object):
    def __init__(self, repository, branch, commit=None):
        self.repository = Repo(repository)
        self.store = self.repository.object_store
        if not commit:
            if branch not in self.repository.refs:
                # The branch does not exist yet
                self.commit = self.tree = None
                return
            commit = self.repository.refs[branch]
        self.commit = self.repository.commit(commit)
        self.tree = self.repository.tree(self.commit.tree)

    def history(self):
        commit = self.commit
        while 1:
            yield commit.id
            if not commit.parents:
                break
            commit = self.repository.commit(commit.parents[0])

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

    def store_commit(self, tree_id, parents, author, message):
        commit = Commit()
        commit.author = author
        commit.committer = 'Pynuts'
        commit.author_time = commit.commit_time = int(time.time())
        commit.author_timezone = commit.commit_timezone = 0
        commit.message = message
        commit.tree = tree_id
        commit.parents = parents or []
        self.store.add_object(commit)
        return commit.id

    def store_directory(self, root):
        tree = Tree()
        for name in os.listdir(root):
            fullname = os.path.join(root, name)
            if os.path.isdir(fullname):
                sub_id = self.store_directory(fullname)
                mode = 040000
            elif os.path.isfile(fullname):
                sub_id = self.store_file(fullname)
                mode = 0100644
            else:
                continue
            tree.add(name, mode, sub_id)
        self.store.add_object(tree)
        return tree.id

    def store_file(self, filename):
        blob = Blob.from_string(open(filename).read())
        self.store.add_object(blob)
        return blob.id

    def store_string(self, bytestring):
        blob = Blob.from_string(bytestring)
        self.store.add_object(blob)
        return blob.id

    def listdir(self, path):
        tree = self._lookup(path)
        if tree.type_name != 'tree':
            raise NotADirectory(path)
        return list(tree)

    def read(self, path):
        blob = self._lookup(path)
        if blob.type_name != 'blob':
            raise NotAFile(path)
        return blob.data

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


class GitLoader(BaseLoader):
    def __init__(self, git):
        self.git = git

    def get_source(self, environment, template):
        if not self.git.isfile(template):
            raise TemplateNotFound(template)
        mtime = self.git.getmtime(template)
        source = self.git.read(template).decode('utf-8')
        # filename might be None
        return source, self.git.filename(template), lambda: \
            self.git.getmtime(template) == mtime
