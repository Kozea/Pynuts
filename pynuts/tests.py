import os.path
import unittest
import contextlib
import shutil
import tempfile
import time

import jinja2

from . import fs


@contextlib.contextmanager
def tempdir(*args, **kwargs):
    directory = tempfile.mkdtemp(*args, **kwargs)
    try:
        yield directory
    finally:
        shutil.rmtree(directory)


class TestFS(unittest.TestCase):
    def test_realfs(self):
        hello_content = ('{% from "sub/name.jinja" import name %}'
                         'Hello {{ name() }}!')
        name_content = '{% macro name() %}from Pynuts{% endmacro %}'
        with tempdir() as temp:
            os.mkdir(os.path.join(temp, 'sub'))
            with open(os.path.join(temp, 'sub', 'name.jinja'), 'w') as fd:
                fd.write(name_content)
            with open(os.path.join(temp, 'hello.jinja'), 'w') as fd:
                fd.write(hello_content)

            now = time.time()
            base = fs.RealFS(temp)

            assert sorted(base.listdir('/')) == ['hello.jinja', 'sub']
            assert sorted(base.listdir('')) == ['hello.jinja', 'sub']
            assert base.listdir('sub') == ['name.jinja']
            self.assertRaises(OSError, base.listdir, '../foo')
            self.assertRaises(OSError, base.listdir, 'inexistent')
            # See https://github.com/mitsuhiko/flask/issues/501
            #self.assertRaises(OSError, base.listdir, '..')

            with base.open('hello.jinja') as fd:
                assert fd.read() == hello_content
            with base.open('sub/name.jinja') as fd:
                assert fd.read() == name_content
                # Files are read-only
                self.assertRaises(IOError, fd.write, 'foo')
            self.assertRaises(TypeError, base.open, 'sub/name.jinja', 'w')

            self.assertRaises(IOError, base.open, 'inexistent')
            self.assertRaises(IOError, base.open, 'sub')

            assert base.isdir('sub')
            assert not base.isdir('hello.jinja')
            assert not base.isdir('sub/name.jinja')
            assert not base.isdir('inexistent')

            assert not base.isfile('sub')
            assert base.isfile('hello.jinja')
            assert base.isfile('sub/name.jinja')
            assert not base.isfile('inexistent')

            assert abs(base.getmtime('hello.jinja') - now) <= 2
            assert abs(base.getmtime('sub') - now) <= 2
            assert abs(base.getmtime('sub/name.jinja') - now) <= 2
            self.assertRaises(OSError, base.getmtime, 'inexistent')

            env = jinja2.Environment(loader=fs.JinjaAbstractFSLoader(base))
            template = env.get_template('hello.jinja')
            assert template.filename == os.path.join(temp, 'hello.jinja')
            assert template.render() == 'Hello from Pynuts!'


if __name__ == '__main__':
    unittest.main()
