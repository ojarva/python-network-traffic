from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nettraffic',
    version='0.0.1',
    description='Small SNMP helper library for network traffic calculations',
    long_description=long_description,
    url='https://github.com/ojarva/python-network-traffic',
    author='Olli Jarva',
    author_email='olli@jarva.fi',
    license='BSD',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
	'Topic :: System :: Networking :: Monitoring',
	'Topic :: System :: Networking',
	'Topic :: System :: Monitoring',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='snmp network traffic',
    packages=["nettraffic"],
    install_requires=[],
    test_suite="tests",

    extras_require = {
        'dev': ['twine', 'wheel'],
    },
)
