from setuptools import setup

setup(
    name = 'ASAB',
    version = '0.1.0',
    packages = ['ASAB', 'ASAB.action', 'ASAB.configuration', 'ASAB.driver', 'ASAB.server', 'ASAB.utility', 'ASAB.test'],
    license = 'LICENSE',
    description = 'This package controls the ASAB setup including all attached devices.',
    long_description = open('README.md').read(),
    install_requires = [
        'fastapi',
        'matplotlib',
        'networkx',
        'numpy',
        'pandas',
        'pyserial',
        'testfixtures',
        'tqdm',
        'uvicorn'
    ]
)