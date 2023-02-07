# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md', 'rb') as f:
    readme_content = f.read()

with open('LICENSE', 'rb') as f:
    license_content = f.read()

setup(
    name='kubespider',
    version='0.1.0',
    description='Unified downloading orchestration system, save your time, enjoy your life.',
    long_description=readme_content,
    author='jwceisn',
    author_email='jwcesign@gmail.com',
    url='https://github.com/jwcesign/kubespider',
    license=license_content,
    packages=find_packages(exclude=('tests', 'docs', '.github', '.config', 'chrome-extension', 'hack'))
)
