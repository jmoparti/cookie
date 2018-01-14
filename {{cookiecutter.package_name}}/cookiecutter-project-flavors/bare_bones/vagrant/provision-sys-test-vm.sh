#!/usr/bin/env bash

set -e

echo "Provisioning the vm used for system testing"

#
# Parse cli args
#

if [[ "${1}" == "py27" ]]; then
    python_interpreter_name="python2.7"
    uwsgi_py_env="python27"
elif [[ "${1}" == "py34" ]]; then
    python_interpreter_name="python3.4"
    uwsgi_py_env="python34"
elif [[ "${1}" == "py35" ]]; then
    python_interpreter_name="python3.5"
    uwsgi_py_env="python35"
else
    echo "ERROR: Unsupported python environment name: '${1}'"
fi

#
# Place holder no-op
#

echo "No-op call to python interpreter help"
${python_interpreter_name} --version
