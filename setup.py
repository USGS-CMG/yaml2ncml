import os
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ["--verbose"]
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


def extract_version():
    version = None
    fdir = os.path.dirname(__file__)
    fnme = os.path.join(fdir, "yaml2ncml", "__init__.py")
    with open(fnme) as fd:
        for line in fd:
            if line.startswith("__version__"):
                _, version = line.split("=")
                version = version.strip()[1:-1]
                break
    return version


rootpath = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return open(os.path.join(rootpath, *parts)).read()


long_description = "{}\n{}".format(read("README.rst"), read("CHANGES.txt"))
LICENSE = read("LICENSE.txt")

with open("requirements.txt") as f:
    require = f.readlines()
install_requires = [r.strip() for r in require]

setup(
    name="yaml2ncml",
    version=extract_version(),
    packages=["yaml2ncml"],
    license=LICENSE,
    description="ncML aggregation from YAML specifications",
    long_description=long_description,
    author="Rich Signell",
    author_email="rsignell@usgs.gov",
    install_requires=install_requires,
    entry_points=dict(console_scripts=["yaml2ncml = yaml2ncml.yaml2ncml:main"]),
    url="https://github.com/rsignell-usgs/yaml2ncml",
    keywords=["YAML", "ncml"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
    ],
    tests_require=["pytest"],
    cmdclass=dict(test=PyTest),
    zip_safe=False,
)
