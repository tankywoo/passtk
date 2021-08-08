#!/usr/bin/env python

import sys
from setuptools import setup, find_packages


entry_points = {
    "console_scripts": [
        "passtk = passtk.passtk:main",
    ]
}

requires = ['pycrypto']
if sys.version_info < (2, 7):
    requires.append('argparse')

setup(
    name="passtk",
    version="0.6.0",
    url="https://github.com/tankywoo/passtk",
    author="Tanky Woo",
    author_email="me@tankywoo.com",
    description="A tool to generate random password.",
    license="MIT License",
    packages=find_packages(),
    install_requires=requires,
    entry_points=entry_points,
)
