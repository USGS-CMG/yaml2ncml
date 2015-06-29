from __future__ import unicode_literals

import subprocess
from unittest import TestCase

from docopt import DocoptExit
from docopt import docopt

from yaml2ncml import yaml2ncml

__doc__ = yaml2ncml.__doc__


class TestYAML2NcML(TestCase):
    """CLI calls."""

    def test_noarg_call(self):
        with self.assertRaises(DocoptExit):
            yaml2ncml.main()

    def test_mandatory_arg(self):
        fin = 'roms.yaml'
        args = docopt(__doc__, [fin])
        self.assertEqual(args['INFILE'], fin)

    def test_optional_arg(self):
        fin = 'test6.ncml'
        fout = '--output=test6.ncml'
        args = docopt(__doc__, [fin, fout])
        self.assertEqual(args['--output'], fout.split('=')[1])

    def test_call(self):
        output = subprocess.check_output(['yaml2ncml', 'roms.yaml'])
        with open('test6.ncml') as f:
            correct = f.read()
        self.assertEqual(correct, output)

    def test_save_file(self):
        subprocess.call(['yaml2ncml',
                         'roms.yaml',
                         '--output=temp.ncml'])
        with open('test6.ncml') as f:
            correct = f.read()
        with open('temp.ncml') as f:
            comp = f.read()
        self.assertEqual(correct, comp)
