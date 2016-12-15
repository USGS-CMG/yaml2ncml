from __future__ import (absolute_import, division, print_function)

import subprocess
import tempfile


def test_call():
    output = subprocess.check_output(['yaml2ncml', 'roms.yaml'])
    with open('base_roms_test.ncml') as f:
        expected = f.read()
    assert output.decode() == expected


def test_save_file():
    outfile = tempfile.mktemp(suffix='.ncml')
    subprocess.call(['yaml2ncml',
                     'roms.yaml',
                     '--output={}'.format(outfile)])
    with open('base_roms_test.ncml') as f:
        expected = f.read()
    with open(outfile) as f:
        output = f.read()
    assert output == expected
