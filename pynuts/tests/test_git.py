import os.path
import unittest
import shutil
import tempfile

import jinja2
from dulwich.repo import Repo
from dulwich.objects import Blob, Tree, Commit
from dulwich.errors import NotGitRepository

from ..git import Git


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

        git.write('templates/hello.jinja', 'Hello, World!')
        git.commit('Alice', 'alice@pynuts.org', 'First commit')
        commit_1 = git.head.id

        git.write('templates/hello.jinja',
            '{% from "sub/name.jinja" import name %}Hello {{ name() }}!')
        git.write('templates/sub/name.jinja',
            '{% macro name() %}from Pynuts{% endmacro %}')
        git.commit('Bob', 'bob@pynuts.org', 'Second commit')
        commit_2 = git.head.id
        assert commit_2 != commit_1
        assert git.head.parents == [commit_1]
        assert git.repository.refs['refs/heads/master'] == commit_2

        # Make sure we read from the filesystem
        git = Git(self.tempdir, branch='master', commit=commit_1)
        env = jinja2.Environment(loader=git.jinja_loader('templates'))
        template = env.get_template('hello.jinja')
        assert template.filename.endswith(
            '/<git commit %s>/templates/hello.jinja' % commit_1)
        assert template.render() == 'Hello, World!'

        git = Git(self.tempdir, branch='master')
        assert git.head.id == commit_2
        env = jinja2.Environment(loader=git.jinja_loader('templates'))
        template = env.get_template('hello.jinja')
        assert template.filename.endswith(
            '/<git commit %s>/templates/hello.jinja' % commit_2)
        assert template.render() == 'Hello from Pynuts!'


if __name__ == '__main__':
    unittest.main()
