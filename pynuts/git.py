# coding: utf8
import os
import time

import jinja2
from werkzeug.utils import cached_property
from dulwich.repo import Repo, Blob, Tree, Commit


class GitException(Exception):
    """Base class for git-related exceptions."""


class NotFoundError(GitException):
    """No such file or directory (blob or tree)."""


class ObjectTypeError(GitException):
    """For example, found a blob where a tree was expected."""


class NoSuchBranchError(GitException):
    """Operation on a branch that does not exist."""


class ConflictError(GitException):
    """Operation on a branch that does not exist."""


class Git(object):
    """Represents a commit and its tree in a git repository.

    This accesses the repository directly without "checking out" files
    into a "working directory".

    This is a higher level wrapper around Dulwich for bare repositories.

    :param repository_path:
        Full path to the repository’s directory in the filesystem.
    :param branch:
        Which branch to use in the repository. (``refs/heads`` is implicit.)
    :param commit_id:
        The SHA1 hash of the commit to use. If given, no check is made that
        the commit is actually reachable from ``branch``. If not given,
        use the latest commit in ``branch``.

    """

    committer = 'Pynuts <pynuts@pynuts.org>'

    def __init__(self, repository_path, branch, commit=None):
        self.repository_path = repository_path
        self.repository = Repo(repository_path)
        self._add_object = self.repository.object_store.add_object
        self.ref = 'refs/heads/' + branch
        commit = commit or self.repository.refs.read_ref(self.ref)
        if commit:
            self.head = self.repository.commit(commit)
            self.tree = self.repository.tree(self.head.tree)
        else:
            self.head = None
            self.tree = Tree()

    def jinja_loader(self, sub_directory=None):
        prefix = sub_directory + '/' if sub_directory else ''

        def get_source(environment, template):
            path = prefix + template
            try:
                source = self.read(path).decode('utf-8')
            except NotFoundError as err:
                raise jinja2.TemplateNotFound(template)
            # Fake filename for tracebacks:
            filename = '%s/<git commit %s>/%s' % (
                self.repository_path, self.head.id, path)
            # Commits are immutable:
            is_uptodate = lambda: True
            return source, filename, is_uptodate

        loader = jinja2.BaseLoader()
        loader.get_source = get_source
        return loader

    def history(self):
        """Return an iterable of commit IDs, starting from this one.

        For merge commits, only the first parent is followed.
        The history is empty if the branch does not exist yet.

        """
        commit = self.head
        if not commit:
            return
        while 1:
            yield commit.id
            if not commit.parents:
                break
            commit = self.repository.commit(commit.parents[0])

    def _split_path(self, path):
        return [part for part in path.encode('utf8').split('/') if part]

    def _lookup(self, path):
        """Recursively walk Tree objects and return the object at this path."""
        parts = self._split_path(path)
        tree = self.tree
        if not parts:
            return tree
        get_object = self.repository.get_object
        for i, part in enumerate(parts):
            if i:
                tree = get_object(sha)
                if tree.type_name != 'tree':
                    raise ObjectTypeError(
                        'Expected a tree, found a %s at %s.'
                        % (tree.type_name, '/'.join(parts[:i])))
            try:
                mode, sha = tree[part]
            except KeyError:
                raise NotFoundError(path)
        return get_object(sha)

    def read(self, path):
        """Return as a byte string the content of the blob at ``path``.

        :raises: NotFoundError, ObjectTypeError

        """
        blob = self._lookup(path)
        if blob.type_name != 'blob':
            raise ObjectTypeError(
                'Expected a blob, found a %s at %s.' % (blob.type_name, path))
        return blob.data

    def write(self, path, bytestring):
        """Update in place self.tree and make sure everything is stored."""
        parts = self._split_path(path)
        if not parts:
            raise ValueError('Empty path: %r' % path)
        tree = self.tree
        traversed_trees = []
        get_object = self.repository.get_object
        for i, name in enumerate(parts[:-1]):
            try:
                mode, sha = tree[name]
            except KeyError:
                sub_tree = Tree()
            else:
                sub_tree = get_object(sha)
                if tree.type_name != 'tree':
                    raise ObjectTypeError(
                        'Expected a tree, found a %s at %s.'
                        % (tree.type_name, '/'.join(parts[:i])))
            traversed_trees.append((tree, name, sub_tree))
            tree = sub_tree

        # TODO: This will also override trees. Raise instead?
        tree[parts[-1]] = 0100644, self.store_bytes(bytestring)
        self._add_object(tree)

        for tree, name, sub_tree in reversed(traversed_trees):
            tree[name] = 040000, sub_tree.id
            self._add_object(tree)

    def commit(self, author_name, author_email, message):
        """Add a new commit in the current branch with this one (if any)
        as a parent, and check that there is no conflict.

        :raises: ConflictError

        """
        new_commit = self.store_commit(
            self.tree.id, author_name, author_email, message,
            parents=[self.head.id] if self.head else [])
        refs = self.repository.refs
        if self.head:
            if not refs.set_if_equals(self.ref, self.head.id, new_commit.id):
                raise ConflictError('%s is not the last commit in %s.'
                                    % (self.head.id, self.ref))
        else:
            if not refs.add_if_new(self.ref, new_commit.id):
                raise ConflictError('%s already exists.' % self.ref)
        self.head = new_commit

    def store_commit(self, tree_id, author_name, author_email,
                     message, parents):
        """Store a new commit and return its ID.

        Note that no branch will point to this commit. You may want to use
        ``commit_into_branch`` instead.

        """
        author = '%s <%s>' % (author_name, author_email)
        commit = Commit()
        commit.author = author.encode('utf8')
        commit.committer = self.committer
        commit.author_time = commit.commit_time = int(time.time())
        # TODO: use the server’s timezone? Something else?
        commit.author_timezone = commit.commit_timezone = 0
        commit.message = message.encode('utf8')
        commit.tree = tree_id
        commit.parents = parents
        self._add_object(commit)
        return commit

    def store_directory(self, root):
        """Recursively store a directory and its content as a tree and
        return its ID.

        Symbolic links are followed. Other special files are ignored

        """
        tree = Tree()
        for name in os.listdir(root):
            fullname = os.path.join(root, name)
            if os.path.isdir(fullname):
                tree.add(name, 040000, self.store_directory(fullname))
            elif os.path.isfile(fullname):
                tree.add(name, 0100644, self.store_file(fullname))
            #else: Ignore special files.
        self._add_object(tree)
        return tree.id

    def store_file(self, filename):
        """Store a file as a blob and return its ID."""
        # TODO: store by chunks without reading everything in memory?
        with open(filename, 'rb') as fd:
            return self.store_bytes(fd.read())

    def store_bytes(self, bytestring):
        """Store a byte string as a blob and return its ID."""
        blob = Blob.from_string(bytestring)
        self._add_object(blob)
        return blob.id
