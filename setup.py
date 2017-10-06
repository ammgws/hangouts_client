from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hangouts_client',
    version='0.1.4',
    description='Class for sending/receiving messages using Hangouts',
    long_description=long_description,
    url='https://github.com/ammgws/hangouts_client',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.6',
    py_modules=['hangoutsclient'],
    install_requires=['sleekxmpp'],
    dependency_links=['https://github.com/ammgws/google_auth/tarball/master']
)
