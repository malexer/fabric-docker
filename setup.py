from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fabric-docker',
    version='0.1',

    description='Docker command-line tool wrapper for Fabric.',
    long_description=long_description,
    url='https://github.com/malexer/fabric-docker',

    author='Alex (Oleksii) Markov',
    author_email='alex@markovs.me',

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Clustering',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='fabric fabfile docker docker-engine',
    packages=['fabric_docker'],
    install_requires=[
        'fabric',
        'pyyaml',
    ],
)
