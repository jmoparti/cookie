#!/usr/bin/env bash

set -e

echo "Installing pre-requisites for build environment"

apt-get install -y git tree wget

# now install tox via pip because of issues like https://github.com/spotify/ramlfications/issues/108 where
# older tox versions packaged with the os are too stale
pip install -U tox
