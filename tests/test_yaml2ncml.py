from __future__ import (absolute_import, division, print_function)

import subprocess
import tempfile

import pytest
import ruamel.yaml as yaml

from yaml2ncml import build


def test_call():
    output = subprocess.check_output(['yaml2ncml', 'roms_0.yaml'])
    with open('base_roms_test.ncml') as f:
        expected = f.read()
    assert output.decode() == expected


def test_save_file():
    outfile = tempfile.mktemp(suffix='.ncml')
    subprocess.call(['yaml2ncml',
                     'roms_0.yaml',
                     '--output={}'.format(outfile)])
    with open('base_roms_test.ncml') as f:
        expected = f.read()
    with open(outfile) as f:
        output = f.read()
    assert output == expected


@pytest.fixture
def load_ymal(fname='roms_1.yaml'):
    with open(fname, 'r') as stream:
        yml = yaml.load(stream, Loader=yaml.RoundTripLoader)
    return yml


def test_bad_yaml():
    with pytest.raises(ValueError):
        yml = load_ymal(fname='roms_1.yaml')
        build(yml)
