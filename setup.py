# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md', 'rb') as f:
    readme_content = f.read()

with open('LICENSE', 'rb') as f:
    license_content = f.read()

setup(
    name='kubespider',
    version='latest',
    description='A global resource download orchestration system, build your home download center.',
    long_description=readme_content,
    author='jwceisn',
    author_email='jwcesign@gmail.com',
    url='https://github.com/opennaslab/kubespider',
    license=license_content,
    packages=find_packages(exclude=('tests', 'docs', '.github', '.config', 'chrome-extension', 'hack', 'kubespider-extension'))
)
