# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='kubespider',
    version='0.1.0',
    description='Kubespider, download from anywhere',
    long_description=readme,
    author='jwceisn',
    author_email='jwcesign@gmail.com',
    url='https://github.com/jwcesign/kubespider',
    license=license,
    packages=find_packages(exclude=('tests', 'docs', '.github', '.kubespider', 'chrome-extension', 'hack'))
)
