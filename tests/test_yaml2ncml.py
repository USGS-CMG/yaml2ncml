import subprocess
import tempfile
from pathlib import Path

import pytest
import ruamel.yaml as yaml

from yaml2ncml import build

path = Path(__file__).parent.resolve()


def test_call():
    fname = str(path.joinpath("roms_0.yaml").resolve())
    output = subprocess.check_output(["yaml2ncml", fname])
    with path.joinpath("base_roms_test.ncml").open() as f:
        expected = f.read()
    assert output.decode() == expected


def test_save_file():
    outfile = tempfile.mktemp(suffix=".ncml")
    fname = str(path.joinpath("roms_0.yaml").resolve())
    subprocess.call(["yaml2ncml", fname, f"--output={outfile}"])
    with path.joinpath("base_roms_test.ncml").open() as f:
        expected = f.read()
    with open(outfile) as f:
        output = f.read()
    assert output == expected


@pytest.fixture
def load_ymal(fname=path.joinpath("roms_1.yaml")):
    with open(fname) as stream:
        yield yaml.load(stream, Loader=yaml.RoundTripLoader)


def test_bad_yaml(load_ymal):
    with pytest.raises(ValueError):
        build(load_ymal)
