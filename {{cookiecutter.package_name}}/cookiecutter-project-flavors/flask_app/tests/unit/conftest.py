"""
Pytest scaffolding config that spans all unit tests
"""

#
# Imports
#

# core python
import logging
import os

# third party
import pytest

# this project
import {{ cookiecutter.root_module_name }}.factory as my_factory

#
# Module variables
#

# logging
_LOGGER = logging.getLogger(__name__)


#
# Hooks
#

@pytest.fixture(scope='function')
def unset_env_variables(monkeypatch):
    # Remove any inherited environment variables
    current_env_var_value = os.getenv(my_factory.FLASK_CONFIG_PATH_ENV_VAR, None)
    if current_env_var_value is not None:
        _LOGGER.debug("Current env var value for var %s is '%s', so unsetting during unit tests",
                      my_factory.FLASK_CONFIG_PATH_ENV_VAR, current_env_var_value)
        monkeypatch.delenv(my_factory.FLASK_CONFIG_PATH_ENV_VAR)
    else:
        _LOGGER.debug("Env var %s is NOT set in the env, so doing nothing",
                      my_factory.FLASK_CONFIG_PATH_ENV_VAR)
