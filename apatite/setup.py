
import os
import imp
from setuptools import setup, find_packages

__author__ = "Mahmoud Hashemi"
__contact__ = "mahmoud@hatnote.com"
__license__ = 'Apache License 2.0'
__url__ = 'https://github.com/mahmoud/apatite'

CUR_PATH = os.path.abspath(os.path.dirname(__file__))
_version_mod_path = os.path.join(CUR_PATH, 'apatite', '_version.py')
_version_mod = imp.load_source('_version', _version_mod_path)
__version__ = _version_mod.__version__

setup(
    name="apatite",
    description="Handy secret management system with a convenient CLI and readable storage format.",
    author=__author__,
    author_email=__contact__,
    url=__url__,
    license=__license__,
    platforms='any',
    version=__version__,
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={'console_scripts': ['apatite = apatite.__main__:main']},
    install_requires=['attrs',
                      'boltons',
                      'ruamel.yaml',
                      'schema']
)

"""
Release process:

* tox  # TODO
* git commit (if applicable)
* Remove dev suffix from apatite/_version.py version
* git commit -a -m "bump version for vX.Y.Z release"
* python setup.py sdist bdist_wheel upload
* git tag -a vX.Y.Z -m "brief summary"
* write CHANGELOG
* git commit
* bump apatite/_version.py version onto n+1 dev
* git commit
* git push

Versions are of the format YY.MINOR.MICRO, see calver.org for more details.
"""
