#!/usr/bin/env bash

set -e

echo "Installing basic Python dependencies"

#
# Parse command line arg(s)
#

python_environments="${1}"
echo "Setting up for these python environments: ${python_environments}"

#
# Install what additional deps you need from apt and set the versions
#

custom_python_versions=""
release_codename=$(lsb_release -sc)
case $release_codename in
    xenial)
        if [[ "${python_environments}" =~ "py27" ]]; then
            apt-get install -y python python-dev python-pip
        fi
        if [[ "${python_environments}" =~ "py34" ]]; then
            # set custom install versions to 3.4
            custom_python_versions="3.4.5"
        fi
        if [[ "${python_environments}" =~ "py35" ]]; then
            # get stock python 3.5 that comes in system packages
            apt-get install -y python3 python3-dev python3-pip
        fi
        if [[ "${python_environments}" =~ "py36" ]]; then
            # set custom install versions to 3.6
            custom_python_versions="3.6.1"
        fi
        ;;
    trusty)
        if [[ "${python_environments}" =~ "py27" ]]; then
            apt-get install -y python python-dev python-pip
        fi
        if [[ "${python_environments}" =~ "py34" ]]; then
            # get stock python 3.4 that comes in system packages
            apt-get install -y python3 python3-dev python3-pip
        fi
        if [[ "${python_environments}" =~ "py35" ]]; then
            # set custom install versions to 3.5
            custom_python_versions="3.5.2"
        fi
        if [[ "${python_environments}" =~ "py36" ]]; then
            # set custom install versions to 3.6
            custom_python_versions="3.6.1"
        fi
        ;;
    *)
        echo "ERROR: unsupported release codename ${release_codename}"
        exit 1
        ;;
esac

if [[ -z "${custom_python_versions}" ]]; then
    echo "No custom python versions needed, using straight from system"
else
    # install build-from-source pre-requisites (based on https://github.com/yyuu/pyenv/wiki)
    apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev llvm libncurses5-dev xz-utils

    # now download each custom python interpreter version and build from source
    cd /tmp
    for custom_python_version in ${custom_python_versions}
    do
        echo "Checking if the python interpreter is already on the machine"
        if [[ ${custom_python_version} =~ ^3\.4\.[0-9]+$ ]]; then
            python_interpreter_name="python3.4"
        elif [[ ${custom_python_version} =~ ^3\.5\.[0-9]+$ ]]; then
            python_interpreter_name="python3.5"
        elif [[ ${custom_python_version} =~ ^3\.6\.[0-9]+$ ]]; then
            python_interpreter_name="python3.6"
        else
            echo "ERROR: Unrecognized python version nickname: '${custom_python_version}'"
            exit 1
        fi
        set +e
        /usr/bin/env ${python_interpreter_name} --version
        exit_code=$?
        set -e
        if [[ ${exit_code} -eq 0 ]]; then
            echo "INFO: Found existing ${python_interpreter_name} so not going to install a new one"
        else
            echo "INFO: Did not find existing ${python_interpreter_name} so going to install one"
            echo "Downloading source for Python ${custom_python_version}"
            wget https://www.python.org/ftp/python/${custom_python_version}/Python-${custom_python_version}.tgz --output-document - | tar -zx

            echo "Installing from downloaded source for Python ${custom_python_version}"
            cd Python-${custom_python_version}
            ./configure
            make altinstall
        fi
    done
fi

# Use the default deb package for virtualenv
apt-get install -y python-virtualenv
