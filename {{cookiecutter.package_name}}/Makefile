#
# Set variables
#

## turn off gnu make parallelism cause of use of tox/virtualenv

.NOTPARALLEL:

## Pick bash ftw

SHELL := /bin/bash

## PIP index urls

{% if cookiecutter.dependency_management_mode == 'public_third_parties' -%}
PIP_INDEX_URL ?= https://pypi.python.org/simple
PIP_EXTRA_INDEX_URL ?= https://pypi.python.org/simple
{% elif cookiecutter.dependency_management_mode == 'managed_in_house' %}
PIP_INDEX_URL ?= https://sysops.wpc.edgecastcdn.net/00AC7B/apt/mirror/pypi-mirror/web/simple
PIP_EXTRA_INDEX_URL ?= https://repoman01.lax.edgecastcdn.net/pips/
{% else %}
WARNING BAD TEMPLATE VALUE for cookiecutter.dependency_management_mode
{% endif %}

## Source files

MAIN_SRC_DIR = {{cookiecutter.root_module_name}}
MAIN_PYC_FILES := $(shell find $(MAIN_SRC_DIR) -name "*.pyc")

## Test files

TESTS_SRC_DIR = tests
TESTS_PYC_FILES := $(shell find $(TESTS_SRC_DIR) -name "*.pyc")
TESTS_PYCACHE_FILES := $(shell find $(TESTS_SRC_DIR) -name "__pycache__")

## Python Environments

DEFAULT_PY2_ENV = py27
DEFAULT_PY3_ENV = $(shell python3 -c 'import sys; print("py{}{}".format(sys.version_info.major, sys.version_info.minor))')

{% if cookiecutter.python_version_mode == 'py27_only' -%}
DEFAULT_PY_ENV ?= $(DEFAULT_PY2_ENV)
TOXENV ?= $(DEFAULT_PY2_ENV)
{% elif cookiecutter.python_version_mode == 'py27_thru_py3' %}
DEFAULT_PY_ENV ?= $(DEFAULT_PY3_ENV)
TOXENV ?= $(DEFAULT_PY2_ENV),$(DEFAULT_PY3_ENV)
{% elif cookiecutter.python_version_mode == 'py3_only' %}
DEFAULT_PY_ENV ?= $(DEFAULT_PY3_ENV)
TOXENV ?= $(DEFAULT_PY3_ENV)
{% else %}
THE COOKIECUTTER TEMPLATE IS BROKEN AND SHOULD NOT HAVE EMITTED THIS
YOU MIGHT HAVE A BAD VALUE FOR cookiecutter.python_version_mode {{ cookiecutter.python_version_mode }}
{% endif %}

## Misc

# ADDOPTS for different test scenarios
PYTEST_ADDOPTS_FOR_UNIT_TESTS = -m unit_test --pylog-output-path .tox_output/unit-tests/pytest.log --cov-report term --cov-report html:.tox_output/unit-tests/htmlcov --junitxml=.tox_output/unit-tests/junit.xml
PYTEST_ADDOPTS_FOR_INT_TESTS = -m integration_test --pylog-output-path .tox_output/int-tests/pytest.log --cov-report term --cov-report html:.tox_output/int-tests/htmlcov --junitxml=.tox_output/int-tests/junit.xml
PYTEST_ADDOPTS_FOR_SYS_TESTS = -m system_test --pylog-output-path .tox_output/sys-tests/pytest.log --cov-report term --cov-report html:.tox_output/sys-tests/htmlcov --junitxml=.tox_output/sys-tests/junit.xml

#
# Modify the environment
#

# set the PIP environment variables
export PIP_INDEX_URL := $(PIP_INDEX_URL)
export PIP_EXTRA_INDEX_URL := $(PIP_EXTRA_INDEX_URL)

#
# Set general targets
#

.DEFAULT_GOAL := all

{% set common_targets = 'all build clean clean_all clean_coverage clean_dist clean_docs clean_logs clean_pyc clean_tox combined_tests develop docs docs_draft format_with_yapf lint tests unit_tests integration_tests system_tests wheel docs test_wheel' -%}

{% if cookiecutter.python_version_mode in ['py27_only'] -%}
.PHONY: {{common_targets}}
{% elif cookiecutter.python_version_mode in ['py3_only'] %}
.PHONY: {{common_targets}} test_multi_py_compat
{% elif cookiecutter.python_version_mode in ['py27_thru_py3'] %}
.PHONY: {{common_targets}} test_multi_py_compat unit_tests_for_py27 unit_tests_for_py3 integration_tests_for_py27 integration_tests_for_py3 system_tests_for_py27 system_tests_for_py3
{% else %}
THE COOKIECUTTER TEMPLATE IS BROKEN AND SHOULD NOT HAVE EMITTED THIS
YOU MIGHT HAVE A BAD VALUE FOR cookiecutter.python_version_mode {{ cookiecutter.python_version_mode }}
{% endif %}

all: clean build lint lint_tests tests docs wheel

#
# Clean targets
#


clean: clean_coverage clean_dist clean_docs clean_logs clean_pyc clean_tox_output

clean_all: clean clean_tox

clean_pyc:
	-rm -r $(MAIN_PYC_FILES) $(TESTS_PYC_FILES) $(TESTS_PYCACHE_FILES)

clean_coverage:
	-rm -r .cache .coverage .coverage.* htmlcov

clean_dist:
	-rm -r .Python env/ bin/ build/ develop-eggs/ dist/ eggs/ .eggs/ lib/ lib64/ parts/ sdist/ var/ *.egg-info/ .installed.cfg *.egg .eggs wheelhouse/*.whl

clean_docs:
	-rm -r sphinx_docs/build/*

clean_logs:
	-rm $(shell find . -name '*.log')

clean_tox: clean_tox_output
	-rm -r .tox

clean_tox_output:
	-rm -r .tox_output

#
# Lint targets
#

lint:
	tox -- lint

lint_tests:
	tox -- lint --src-dir=tests --errors-only

#
# Build related targets
#

## run setuptools build command

build:
	tox -- build

## run setuptools develop command

develop:
	tox -- develop

## run sphinx doc builds via setuptools

# make the docs for real with strict sphinx config

docs:
	tox -e $(DEFAULT_PY_ENV) -- docs --strict-sphinx-build
	./make-html-docs-archive.sh

# make a draft with lax sphinx config

docs_draft:
	tox -e $(DEFAULT_PY_ENV) -- docs

## build a wheel via setuptools

wheel: clean_dist
	tox -e $(DEFAULT_PY_ENV) -- bdist_wheel

#
# Testing targets
#

## required target for basic testing

tests:
	@echo "Runs all tests"
	echo > pytest.log
	tox -- test

## optional targets for detailed/focused testing

unit_tests:
	@echo "Runs unit tests only and with detailed reporting output under .tox_output/unit-tests"
	mkdir -p .tox_output/unit-tests
	echo > .tox_output/unit-tests/pytest.log
	export PYTEST_ADDOPTS="$(PYTEST_ADDOPTS_FOR_UNIT_TESTS)" && tox -e $(DEFAULT_PY_ENV) -- test

integration_tests:
	@echo "Runs integration tests only and with detailed reporting output under .tox_output/int-tests"
	mkdir -p .tox_output/int-tests
	echo > .tox_output/int-tests/pytest.log
	export PYTEST_ADDOPTS="$(PYTEST_ADDOPTS_FOR_INT_TESTS)" && tox -e $(DEFAULT_PY_ENV) -- test

system_tests:
	@echo "Runs system tests only and with detailed reporting output under .tox_output/int-tests"
	mkdir -p .tox_output/sys-tests
	echo > .tox_output/sys-tests/pytest.log
	export PYTEST_ADDOPTS="$(PYTEST_ADDOPTS_FOR_SYS_TESTS)" && tox -e $(DEFAULT_PY_ENV) -- test

#
# Extra targets
#

## Test the install of the wheel locally

test_wheel: wheel
	./test-wheel.sh $(DEFAULT_PY_ENV)

## Optionally format your code with yapf

format_with_yapf:
	./format-with-yapf.sh
