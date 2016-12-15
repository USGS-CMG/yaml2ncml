from __future__ import (absolute_import, division, print_function)

import subprocess

import pytest
from docopt import DocoptExit
from docopt import docopt

from yaml2ncml import yaml2ncml

__doc__ = yaml2ncml.__doc__


# CLI.
def test_noarg_call():
    with pytest.raises(DocoptExit):
        yaml2ncml.main()


def test_mandatory_arg():
    fin = 'roms.yaml'
    args = docopt(__doc__, [fin])
    assert args['INFILE'] == fin


def test_optional_arg():
    fin = 'test6.ncml'
    fout = '--output=test6.ncml'
    args = docopt(__doc__, [fin, fout])
    assert args['--output'] == fout.split('=')[1]


# ncml.
def test_call():
    output = subprocess.check_output(['yaml2ncml', 'roms.yaml'])
    with open('test6.ncml') as f:
        expected = f.read()
    assert output.decode() == expected


def test_save_file():
    subprocess.call(['yaml2ncml',
                     'roms.yaml',
                     '--output=temp.ncml'])
    with open('test6.ncml') as f:
        expected = f.read()
    with open('temp.ncml') as f:
        output = f.read()
    assert output == expected
