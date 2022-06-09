import pytest
from docopt import docopt

from yaml2ncml import yaml2ncml

__doc__ = yaml2ncml.__doc__


def test_noarg_call():
    with pytest.raises(SystemExit):
        yaml2ncml.main()


def test_mandatory_arg():
    fin = "roms.yaml"
    args = docopt(__doc__, [fin])
    assert args["INFILE"] == fin


def test_optional_arg():
    fin = "test6.ncml"
    fout = "--output=test6.ncml"
    args = docopt(__doc__, [fin, fout])
    assert args["--output"] == fout.split("=")[1]
