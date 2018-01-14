#!/usr/bin/env bash

#
# Test the sys test vm in the emitted template's Vagrantfile
#

# NOTE:
# You cannot use the pytest-xdist with this set of tests
# because virtualbox itself only knows 1 vm name and you cannot run two
# different tests against the same vm name at the same time.

set -e
source .virtualenv/bin/activate
export PYTEST_LOG_PATH=output/test_vagrant_sys_test_vm.log
py.test -p no:xdist -x -m "custom_vagrant_test and custom_sys_test_vm_test" --self-contained-html --html=output/test_vagrant_sys_test_vm.report.html tests
