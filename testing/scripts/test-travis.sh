#!/usr/bin/env bash

#
# Run all non-smoke tests of the emitted template's travis configs
#

set -e
source .virtualenv/bin/activate
export PYTEST_LOG_PATH=output/test_travis.log
py.test -n auto -x -m "custom_travis_test and not custom_smoke_test" --self-contained-html --html=output/test_travis.report.html tests
