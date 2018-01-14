#!/usr/bin/env bash

#
# Run all non-smoke, cookiecutter api using,  tests of the emitted template's make targets
#

set -e
source .virtualenv/bin/activate
export PYTEST_LOG_PATH=output/test_make_via_api.log
py.test -n auto -x -m "custom_make_test and custom_api_test and not custom_smoke_test" --self-contained-html --html=output/test_make_via_api.report.html tests
