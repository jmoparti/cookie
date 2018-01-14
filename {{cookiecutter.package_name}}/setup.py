# -*- coding: utf-8 -*-

#
# Import core python modules
#

from setuptools import setup

# pylint: disable=no-name-in-module,no-member
import distutils.core

# misc
import codecs
import logging
import os
import subprocess
import sys

#
# Declare constants
#

ROOT_MODULE_NAME = '{{cookiecutter.root_module_name}}'
PACKAGE_NAME = '{{cookiecutter.package_name}}'
LICENSE_NAME = 'Proprietary - Copyright (C) VDMS/Edgecast',

#
# Config logging
#

logging.basicConfig(
    stream=sys.stderr,
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] [%(funcName)s] -- %(message)s')

#
# Read additional data
#

PACKAGE_VERSION = open('VERSION').readline().strip()

#
# Custom Command Classes
#

class PylintCommand(distutils.core.Command):
    """Custom command to run pylint"""
    description = 'run Pylint'
    user_options = [
        ('pylintrc=', None, "The pylintrc file to use"),
        ('errors-only', None, "Use errors only mode"),
        ('src-dir=', None, "Source directory, defaults to {}".format(ROOT_MODULE_NAME)),
    ]

    def initialize_options(self):
        """Set default values for options."""
        self.pylintrc = None
        self.errors_only = None
        self.src_dir = None

    def finalize_options(self):
        """Post-process options."""
        if not self.pylintrc:
            self.pylintrc = os.path.join('.', 'pylintrc')
        if not self.errors_only:
            self.errors_only = False
        else:
            self.errors_only = True
        if not self.src_dir:
            self.src_dir = ROOT_MODULE_NAME

    def run(self):
        """Run command."""
        lint_args = [
            'pylint',
            '--rcfile={}'.format(self.pylintrc),
            self.src_dir,
        ]
        if self.errors_only:
            lint_args.append('--errors-only')
        try:
            subprocess.check_call(lint_args)
        except subprocess.CalledProcessError as error:
            sys.exit(error.returncode)


class SphinxDocCommand(distutils.core.Command):
    """Custom command to run sphinx-build because sphinx's own BuildDoc is missing -W"""
    description = 'run sphinx-build'
    user_options = [
        ('strict-sphinx-build', None, 'Run sphinx-build in strict mode (-W)'),
    ]

    def initialize_options(self):
        """Set default values for options."""
        self.strict_sphinx_build = None

    def finalize_options(self):
        """Post-process options."""
        if self.strict_sphinx_build:
            self.strict_sphinx_build = True
        else:
            self.strict_sphinx_build = False

    def run(self):
        """Run command."""
        sphinx_build_args = [
            'sphinx-build',
            '-v',
        ]
        if self.strict_sphinx_build:
            sphinx_build_args.append('-W')
        sphinx_build_args.extend([
            '-b',
            'html',
            '-Dproject={}'.format(PACKAGE_NAME),
            '-Dversion={}'.format(PACKAGE_VERSION),
            '-Drelease={}'.format(PACKAGE_VERSION),
            'sphinx_docs/source',
            'sphinx_docs/build/html',
        ])
        try:
            subprocess.check_call(sphinx_build_args)
        except subprocess.CalledProcessError as error:
            sys.exit(error.returncode)


#
# Custom helper functions
#

def my_find_packages(*args):
    """A custom package finder to use instead of setuptools.find_packages()"""
    packages = []
    for root_module_dir in args:
        for root, dirs, files in os.walk(root_module_dir):
            if '__init__.py' in files:
                packages.append(root)
    return packages


#
# Call setup
#

setup(
    #
    # The name of the Python package for this project.  Not necessarily the same name as
    # that of the top level module in this project.
    #
    name=PACKAGE_NAME,

    #
    # Versions should comply with PEP440
    #
    version=PACKAGE_VERSION,

    #
    # Set the short description
    #
    description='{{cookiecutter.project_short_description}}',

    #
    # Set the long description using the outboard description file
    #
    long_description= open('DESCRIPTION.rst').readline().strip(),

    #
    # The project's main homepage.
    # In our context, it would be the project's home on our internal github
    #
    url='https://localhost/',

    #
    # Author details
    #
    author='{{cookiecutter.author_name}}',
    author_email='{{cookiecutter.author_email}}',

    #
    # Short name for the license for this software
    #
    license=LICENSE_NAME,

    #
    # Classifier labels for this project
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    #
    classifiers=[
        #
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        #
        'Development Status :: 5 - Production/Stable',

        #
        # Indicate who your project is intended for
        #
        'Intended Audience :: VDMS/EdgeCast SysOps Developers',

        #
        # Pick your license as you wish (should match "license" above)
        #
        'License :: Proprietary :: {}'.format(LICENSE_NAME),

        #
        # Specify the Python versions you support here.
        #
{%- if cookiecutter.python_version_mode in ['py27_only', 'py27_thru_py3'] %}
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
{%- endif -%}
{%- if cookiecutter.python_version_mode in ['py3_only', 'py27_thru_py3'] %}
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
{%- endif %}

        #
        # A guard against being accidently uploaded to the public PyPI site
        #
        'Private :: Do Not Upload',
    ],

    #
    # What does your project relate to?
    #
    keywords='development',

    #
    # This stanza tells setuptools where to find your projects source.
    # Note that this is not supposed to include your test's source.
    #
    packages=my_find_packages('{{cookiecutter.root_module_name}}'),

    #
    # Dependencies required on installation of this package
    #
    # Use the ``requirements.txt`` file included in this repo for
    # the pip requirements specifications for this stanza.
    #
    install_requires=[
        "enum34 >= 1.0.4, < 2.0.0 ; python_version < '3.0'",
{%- if cookiecutter.project_flavor == 'flask_app' %}
        "Flask >= 0.11.1, < 0.12.0",
{%- endif %}
    ],

    #
    # Dependencies required during testing
    #
    # Use the ``test_requirements.txt`` file included in this repo for
    # the pip requirements specifications for this stanza.
    #
    tests_require=[
        "coverage >= 4.1, < 5.0",
        "pytest >= 3.0.4, < 4.0.0",
        "pytest-cov >= 2.3.1, < 3.0.0",
        # NOTE:
        # - We are using the backport of mock regardless of which Python
        #   version is targeted by this project.
        # - This reduces the number of if/then variations since
        #   they renamed `mock` module to `unittest.mock` in Python 3.3+
        # - It also allows you to side-step buggy versions of the library that
        #   are included in some versions of the Python 3.x interpreter.
        "mock >= 2.0.0, < 3.0.0",
    ],

    #
    # Dependencies required by setup.py itself (this file)
    #
    # - These dependencies are installed via easy_install and NOT pip when
    #   setuptools runs
    # - If you have particular dependencies that need to be on the box before
    #   your setup.py is run, then describe them in a requirements.txt file
    #   and make sure your runtime (virtualenv if at all possible), is
    #   pre-populated with those requirements.
    # - Advice is not to use the `setup_requires` option unless you really really know what you
    #   you are doing with Python packaging etc.
    #
    setup_requires=[],

    #
    # If there are data files included in your packages that need to be
    # installed, specify them here.
    #
    package_data={
    },
    include_package_data=True,

    #
    # non-package data files
    #
    data_files=[
    ],

    #
    # This library provides no executable scripts
    #
{%- if cookiecutter.project_flavor in ['cli_app'] %}
    entry_points={
        'console_scripts': [
            '{{cookiecutter.root_module_name}}_cli={{cookiecutter.root_module_name}}.cli:main',
        ],
    },
{%- else -%}
    entry_points={},
{%- endif -%}

    #
    # Wire up the custom command classes
    #
    cmdclass={
        'docs': SphinxDocCommand,
        'lint': PylintCommand,
    },
    command_options={
    },
)
