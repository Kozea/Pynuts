import os.path
import unittest
import contextlib
import shutil
import tempfile
import time

import jinja2
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit
from dulwich.errors import NotGitRepository

from . import fs


@contextlib.contextmanager
def tempdir(*args, **kwargs):
    directory = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


class TestFS(unittest.TestCase):
    hello1_content = 'Hello, World!'
    hello2_content = ('{% from "sub/name.jinja" import name %}'
                     'Hello {{ name() }}!')
    name_content = '{% macro name() %}from Pynuts{% endmacro %}'

    def test_realfs(self):
        with tempdir() as temp:
            os.mkdir(os.path.join(temp, 'sub'))
            with open(os.path.join(temp, 'sub', 'name.jinja'), 'w') as fd:
                fd.write(self.name_content)
            with open(os.path.join(temp, 'hello.jinja'), 'w') as fd:
                fd.write(self.hello2_content)

            now = time.time()
            self._check_fs(directory=fs.RealFS(temp), now=time.time(),
                           hello_filename=os.path.join(temp, 'hello.jinja'))

    def test_git(self):
        with tempdir() as temp:
            repo = Repo.init_bare(temp)
            store = repo.object_store

            blob1 = Blob.from_string(self.hello1_content)
            tree1 = Tree()
            tree1.add('hello.jinja', 0100644, blob1.id)
            commit1 = Commit()
            commit1.author = commit1.committer = 'Pynuts'
            commit1.author_time = commit1.commit_time = 42
            commit1.author_timezone = commit1.commit_timezone = 0
            commit1.message = 'First commit'
            commit1.tree = tree1.id

            blob2 = Blob.from_string(self.name_content)
            tree2 = Tree()
            tree2.add('name.jinja', 0100644, blob2.id)
            blob3 = Blob.from_string(self.hello2_content)
            tree3 = Tree()
            tree3.add('hello.jinja', 0100644, blob3.id)
            tree3.add('sub', 040000, tree2.id)
            commit2 = Commit()
            commit2.author = commit2.committer = 'Pynuts'
            commit2.author_time = commit2.commit_time = 42
            commit2.author_timezone = commit2.commit_timezone = 0
            commit2.message = 'Second commit'
            commit2.tree = tree3.id
            commit2.parents = [commit1.id]

            store.add_object(blob1)
            store.add_object(blob2)
            store.add_object(blob3)
            store.add_object(tree1)
            store.add_object(tree2)
            store.add_object(tree3)
            store.add_object(commit1)
            store.add_object(commit2)
            repo.refs['refs/heads/master'] = commit2.id
            del repo
            now = time.time()

            repo_bis = Repo(temp)
            assert repo_bis.ref('refs/heads/master') == repo_bis.head()
            master = repo_bis.head()
            master_parent, = repo_bis.get_parents(master)

            self.assertRaises(NotGitRepository, fs.GitFS,
                os.path.dirname(__file__), master_parent)
            self.assertRaises(KeyError, fs.GitFS, temp, '42' * 20)
            self._check_fs(directory=fs.GitFS(temp, master), now=42,
                           hello_filename='<commit %s>/hello.jinja' % master)

            env = jinja2.Environment(
                loader=fs.JinjaAbstractFSLoader(fs.GitFS(temp, master_parent)))
            template = env.get_template('hello.jinja')
            assert template.filename == (
                '<commit %s>/hello.jinja' % master_parent)
            assert template.render() == 'Hello, World!'

    def _check_fs(self, directory, now, hello_filename):
        listdir = directory.listdir
        assert sorted(listdir('/')) == ['hello.jinja', 'sub']
        assert sorted(listdir('')) == ['hello.jinja', 'sub']
        assert listdir('sub') == ['name.jinja']
        self.assertRaises(fs.FileNotFound, listdir, '../foo')
        self.assertRaises(fs.FileNotFound, listdir, 'inexistent')
        self.assertRaises(fs.FileNotFound, listdir, 'inexistent/foo')
        self.assertRaises(fs.FileNotFound, listdir, 'sub/inexistent')
        self.assertRaises(fs.NotADirectory, listdir, 'hello.jinja')
        self.assertRaises(fs.NotADirectory, listdir, 'sub/name.jinja')
        # See https://github.com/mitsuhiko/flask/issues/501
        #self.assertRaises(OSError, listdir, '..')

        with directory.open('hello.jinja') as fd:
            assert fd.read() == self.hello2_content
        with directory.open('sub/name.jinja') as fd:
            assert fd.read() == self.name_content
        self.assertRaises(TypeError, directory.open, 'sub/name.jinja', 'w')

        self.assertRaises(fs.FileNotFound, directory.open, 'inexistent')
        self.assertRaises(fs.FileNotFound, directory.open, 'inexistent/foo')
        self.assertRaises(fs.FileNotFound, directory.open, 'sub/inexistent')
        self.assertRaises(fs.NotAFile, directory.open, 'sub')

        assert directory.isdir('sub')
        assert not directory.isdir('hello.jinja')
        assert not directory.isdir('sub/name.jinja')
        assert not directory.isdir('inexistent')

        assert not directory.isfile('sub')
        assert directory.isfile('hello.jinja')
        assert directory.isfile('sub/name.jinja')
        assert not directory.isfile('inexistent')

        assert abs(directory.getmtime('hello.jinja') - now) <= 2
        assert abs(directory.getmtime('sub') - now) <= 2
        assert abs(directory.getmtime('sub/name.jinja') - now) <= 2
        self.assertRaises(fs.FileNotFound, directory.getmtime, 'inexistent')

        env = jinja2.Environment(loader=fs.JinjaAbstractFSLoader(directory))
        template = env.get_template('hello.jinja')
        assert template.filename == hello_filename
        assert template.render() == 'Hello from Pynuts!'

if __name__ == '__main__':
    unittest.main()
