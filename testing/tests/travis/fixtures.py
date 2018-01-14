# -*- coding: utf-8 -*-
"""
Common fixtures
"""

#
# Imports
#

# import core
import copy
import json
import logging
import os

# import third party
import pytest

# this project

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)

# constants
GITHUB_TOKEN_ENV_VAR = "COOKIECUTTER_SYSOPS_PYTHON_PACKAGE_TEST_GITHUB_TOKEN"

#
# Fixtures
#


@pytest.fixture(scope="session")
def github_token_for_travis_tests():
    """Grab an environment variable with travis test stuff"""
    value = os.environ.get(GITHUB_TOKEN_ENV_VAR, None)
    if value is None:
        pytest.skip("Missing environment variable {}".format(GITHUB_TOKEN_ENV_VAR))
    elif len(value) == 0:
        pytest.skip("Environment variable {} was set to empty string".format(GITHUB_TOKEN_ENV_VAR))
    else:
        _LOGGER.debug("Got mostly valid value for env var %s", GITHUB_TOKEN_ENV_VAR)
    return value

