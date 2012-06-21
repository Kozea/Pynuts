# coding: utf8
import os
import io
import time
import urllib
import urlparse
import mimetypes

import jinja2
from weasyprint.urls import register_opener
from dulwich.repo import Repo as BaseRepo, Blob, Tree, Commit


class GitException(Exception):
    """Base class for git-related exceptions."""


class NotFoundError(GitException):
    """No such file or directory (blob or tree)."""


class ObjectTypeError(GitException):
    """For example, found a blob where a tree was expected."""


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
        Which branch to use in the repository. (`refs/heads` is implicit.)
    :param commit_id:
        The SHA1 hash of the commit to use. If given, no check is made that
        the commit is actually reachable from `branch`. If not given,
        use the latest commit in `branch`.

    """

    committer = 'Pynuts <pynuts@pynuts.org>'

    def __init__(self, repository, branch=None, commit=None):
        self.repository = repository
        self._add_object = repository.object_store.add_object
        self._get_object = repository.get_object

        if branch:
            self.ref = 'refs/heads/' + branch
            commit = commit or repository.refs.read_ref(self.ref)
        else:
            self.ref = None

        if commit:
            self.head = repository.commit(commit)
            self.tree = repository.tree(self.head.tree)
        else:
            self.head = None
            self.tree = Tree()

    def jinja_loader(self, sub_directory=None):
        prefix = sub_directory + '/' if sub_directory else ''

        def get_source(environment, template):
            path = prefix + template
            try:
                source = self.read(path).decode('utf-8')
            except NotFoundError:
                raise jinja2.TemplateNotFound(template)
            # Fake filename for tracebacks:
            filename = '%s/<git commit %s>/%s' % (
                self.repository.path, self.head.id, path)
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

    def _lookup(self, path, create_trees=False):
        parts = [part for part in path.encode('utf8').split('/') if part]
        if not parts:
            raise ValueError('empty path: %r' % path)

        last_i = len(parts) - 1
        tree = self.tree
        steps = []
        for i, name in enumerate(parts):
            if name in tree:
                _mode, sha = tree[name]
                obj = self._get_object(sha)
                # All but the last part must be trees
                if i < last_i and obj.type_name != 'tree':
                    path = '/'.join(name for _, name, _ in steps)
                    raise ObjectTypeError("'%s' is a %s, expected a tree."
                                          % (path, obj.type_name))
            elif create_trees:
                obj = Tree() if i < last_i else None
            else:
                raise NotFoundError(path)
            steps.append((tree, name, obj))
            tree = obj
        return steps, obj

    def read(self, path):
        """Return as a byte string the content of the blob at `path`.

        :raises: NotFoundError, ObjectTypeError

        """
        _, blob = self._lookup(path)
        if blob.type_name != 'blob':
            raise ObjectTypeError("'%s' is a %s, expected a blob."
                                  % (path, blob.type_name))
        return blob.data

    def write(self, path, bytestring):
        """Update in place self.tree and make sure everything is stored.

        :param path: path to the file to write
        :param bytestring: content of the file to write

        """
        steps, _ = self._lookup(path, create_trees=True)
        tree, name, obj = steps.pop()
        if obj and obj.type_name != 'blob':
            raise ObjectTypeError('Will not overwrite a %s at %s'
                                  % (obj.type_name, path))

        tree[name] = 0100644, self.store_bytes(bytestring).id
        self._add_object(tree)

        for tree, name, sub_tree in reversed(steps):
            tree[name] = 040000, sub_tree.id
            self._add_object(tree)
        # self.tree ends up updated in-place.

    def commit(self, author_name, author_email, message):
        """Add a new commit in the current branch with this one (if any)
        as a parent, and check that there is no conflict.

        :param author_name: commit author name
        :param author_email: commit author email
        :param message: commit message

        :raises: ConflictError

        """
        if not self.ref:  # pragma: no cover
            raise GitException('Not on a branch.')
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
                     message, parents, timezone=None):
        """Store a new commit and return its ID.

        Note that no branch will point to this commit. You may want to use
        `commit_into_branch` instead.

        :param tree_id: git tree id
        :param author_name: commit author name
        :param author_email: commit author email
        :param message: commit message
        :param parents: parent commits


        """
        author = '%s <%s>' % (author_name, author_email)
        commit = Commit()
        commit.author = author.encode('utf8')
        commit.committer = self.committer
        commit.author_time = commit.commit_time = int(time.time())
        if timezone is None:
            # UTC. TODO: use the server’s timezone? Something else?
            timezone = 0
        commit.author_timezone = commit.commit_timezone = timezone
        commit.message = message.encode('utf8')
        commit.tree = tree_id
        commit.parents = parents
        self._add_object(commit)
        return commit

    def store_directory(self, root):
        """Recursively store a directory and its content as a tree and
        return its ID.

        Symbolic links are followed. Other special files are ignored

        :param root: git tree root

        """
        tree = Tree()
        for name in os.listdir(root):
            fullname = os.path.join(root, name)
            if os.path.isdir(fullname):
                tree.add(name, 040000, self.store_directory(fullname).id)
            elif os.path.isfile(fullname):
                tree.add(name, 0100644, self.store_file(fullname).id)
            #else: Ignore special files.
        self._add_object(tree)
        return tree

    def store_file(self, filename):
        """Store a file as a blob and return its ID.

        :param filename: name of the file to store

        """
        # TODO: store by chunks without reading everything in memory?

        with open(filename, 'rb') as fd:
            return self.store_bytes(fd.read())

    def store_bytes(self, bytestring):
        """Store a byte string as a blob and return its ID.

        :param bytestring: byte string to store

        """
        blob = Blob.from_string(bytestring)
        self._add_object(blob)
        return blob

    def make_weasyprint_url(self, path):
        """Return an URL that can be used in WeasyPrint for `path` at the
        current commit. Uncommited changes will *not* be visible.

        This does not checks that a blob actually exists at `path`
        in the commit.

        """
        return 'git://{repo}-{commit}/{path}'.format(
            repo=id(self.repository),
            commit=self.head.id,
            path=urllib.quote(path))


@register_opener('git')
def git_urlopen(url):
    url = urlparse.urlsplit(url)
    repo_id, commit_hash = url.netloc.split('-', 1)
    git = Git(REPOS_BY_ID[int(repo_id)], commit=commit_hash)
    path = urllib.unquote(url.path)
    # TODO: avoid reading everything in memory at once?
    fileobj = io.BytesIO(git.read(path))
    mimetype, _ = mimetypes.guess_type(path)
    charset = None  # unknown
    return fileobj, mimetype, charset


urlparse.uses_relative.append('git')

REPOS_BY_ID = {}


class Repo(BaseRepo):
    def __init__(self, path):
        super(Repo, self).__init__(path)
        REPOS_BY_ID[id(self)] = self
