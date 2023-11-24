from setuptools import setup
from setuptools import find_packages

setup(
    name='kubespider-source-provider-manager',
    version='0.1.0',
    python_requires=">=3.6.0",
    packages=find_packages(),
    install_requires=[
        'pyyaml==6.0.1'
    ],
)
