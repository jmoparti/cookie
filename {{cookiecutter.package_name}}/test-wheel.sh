#!/usr/bin/env bash

#
# Test making the wheel and then installing it
#

set -e

python_package_name="{{ cookiecutter.package_name }}"
wheel_file_pattern="{{ cookiecutter.package_name|replace('-', '_') }}-*.whl"

#
# Parse command line arg(s)
#

python_environment="${1}"
echo "Testing the wheel in this python environment: ${python_environment}"

#
# Init all the supported tox environments
#
tox --notest -e ${python_environment}

#
# test the wheel install
#

source .tox/${python_environment}/bin/activate
pip wheel --wheel-dir=./wheelhouse -r dev-requirements.txt
pip install --no-index --find-links=./wheelhouse dist/${wheel_file_pattern}
pip freeze | grep ${python_package_name}
pip uninstall -y ${python_package_name}
