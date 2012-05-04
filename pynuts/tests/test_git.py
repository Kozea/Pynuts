import os.path
import unittest
import shutil
import tempfile

import jinja2
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit
from dulwich.errors import NotGitRepository

from ..git import Git, ObjectTypeError, NotFoundError, ConflictError


class TestGit(unittest.TestCase):
    hello1_content = 'Hello, World!'
    hello2_content = ('{% from "sub/name.jinja" import name %}'
                     'Hello {{ name() }}!')
    name_content = '{% macro name() %}from Pynuts{% endmacro %}'

    def setUp(self):
        self.tempdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tempdir)

    def test_git(self):
        self.assertRaises(NotGitRepository, Git, self.tempdir, branch='master')
        Repo.init_bare(self.tempdir)
        git = Git(self.tempdir, branch='master')
        git2 = Git(self.tempdir, branch='master')

        def get_hello():
            env = jinja2.Environment(loader=git.jinja_loader('templates'))
            return env.get_template('hello.jinja')

        self.assertRaises(jinja2.TemplateNotFound, get_hello)
        self.assertRaises(ValueError, git.write, '', 'foo')  # empty path

        git.write('templates/hello.jinja', 'Hello, World!')
        self.assertRaises(ObjectTypeError, git.write, 'templates', 'foo')
        self.assertRaises(ObjectTypeError, git.write,
                          'templates/hello.jinja/foo', 'foo')
        assert list(git.history()) == []
        git.commit('Alice', 'alice@pynuts.org', 'First commit')
        commit_1 = git.head.id
        assert list(git.history()) == [commit_1]
        self.assertRaises(ConflictError, git2.commit,
                          'Alice', 'alice@pynuts.org', '(not) First commit')

        git.write('templates/hello.jinja',
            '{% from "sub/name.jinja" import name %}Hello {{ name() }}!')
        git.write('templates/sub/name.jinja',
            '{% macro name() %}from Pynuts{% endmacro %}')
        git.commit('Bob', 'bob@pynuts.org', 'Second commit')
        commit_2 = git.head.id
        assert commit_2 != commit_1
        assert git.head.parents == [commit_1]
        assert git.repository.refs['refs/heads/master'] == commit_2
        assert list(git.history()) == [commit_2, commit_1]

        # Make sure we read from the filesystem
        git = Git(self.tempdir, branch='master', commit=commit_1)

        self.assertRaises(ConflictError, git.commit,
                          'Bob', 'bob@pynuts.org', '(not) Second commit')

        self.assertRaises(ValueError, git.read, '')
        self.assertRaises(ValueError, git.read, '/')
        self.assertRaises(ObjectTypeError, git.read, 'templates')
        self.assertRaises(ObjectTypeError, git.read,
                          'templates/hello.jinja/foo')
        self.assertRaises(NotFoundError, git.read, 'foo')
        self.assertRaises(NotFoundError, git.read, 'foo/bar')
        self.assertRaises(NotFoundError, git.read, 'templates/bar')
        assert git.read('templates/hello.jinja') == 'Hello, World!'
        assert git.read('/templates//hello.jinja') == 'Hello, World!'

        template = get_hello()
        assert template.filename.endswith(
            '/<git commit %s>/templates/hello.jinja' % commit_1)
        assert template.render() == 'Hello, World!'

        git = Git(self.tempdir, branch='master')
        assert git.head.id == commit_2
        template = get_hello()
        assert template.filename.endswith(
            '/<git commit %s>/templates/hello.jinja' % commit_2)
        assert template.render() == 'Hello from Pynuts!'


        git = Git(self.tempdir, branch='inexistent')
        git.tree = git.store_directory(os.path.join(self.tempdir, 'refs'))
        assert git.read('heads/master').strip() == commit_2
