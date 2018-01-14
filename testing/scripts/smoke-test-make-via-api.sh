#!/usr/bin/env bash

#
# Smoke (not full) test via the cookiecutter Python api
#

set -e
source .virtualenv/bin/activate
export PYTEST_LOG_PATH=output/smoke_test_make_via_api.log
py.test -p no:xdist -x -m "custom_smoke_test and custom_make_test and custom_api_test" --self-contained-html --html=output/smoke_test_make_via_api.report.html tests
