#!/usr/bin/env python
from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, '..', 'version.py')) as f:
    exec(f.read())

def find_api(name):
    return f"{name} @ file://localhost/{here}/../{name}#egg={name}"

api = find_api('microns-manual-proofreading-api')

setup(
    name='microns-manual-proofreading',
    version=__version__,
    description='Manual proofreading data for MICrONS',
    author='Stelios Papadopoulos',
    author_email='spapadop@bcm.edu',
    packages=find_packages(exclude=[]),
    install_requires=['numpy', 'scipy', 'tqdm', 'pandas', 'seaborn', 'matplotlib', api]
)