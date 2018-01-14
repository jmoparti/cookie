#!/usr/bin/env bash

#
# Test making the wheel and then installing it
#

set -e

# Default Python Environment
{% if cookiecutter.python_version_mode == 'py27_only' -%}
DEFAULT_PY_ENV=py27
{% elif cookiecutter.python_version_mode == 'py3_only' %}
DEFAULT_PY_ENV=py34
{% elif cookiecutter.python_version_mode in ['py27_thru_py3'] %}
DEFAULT_PY_ENV=py34
{% endif %}

#
# Init all the supported tox environments and activate the default one
#
tox --notest
source .tox/${DEFAULT_PY_ENV}/bin/activate

#
# Use yapf to format source code
#

set +e
yapf --in-place --recursive setup.py {{cookiecutter.root_module_name}} tests
set -e

pylint --errors-only setup.py
python setup.py lint
python setup.py lint --src-dir=tests --errors-only
