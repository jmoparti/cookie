# -*- coding: utf-8 -*-

# import core
import logging
import os
import sys
import tempfile

# import third party
import mock
import pytest

# import your code under test
import {{ cookiecutter.root_module_name }}.factory as my_factory

#
# Module variables
#

# marks everything in here as a unit test
pytestmark = pytest.mark.unit_test

# logger for test scaffolding
_LOGGER = logging.getLogger(__name__)


#
# Tests themselves
#

def test_wout_env_var(unset_env_variables):
    """Try building a flask app obj without the env variable being set"""
    _LOGGER.info("Begin test")

    # Make sure the env variable is NOT set
    assert os.getenv(my_factory.FLASK_CONFIG_PATH_ENV_VAR, None) is None

    # now run the factory
    app = my_factory.build_app()
    assert app

    _LOGGER.info("Finished test")


def test_with_env_var(unset_env_variables, monkeypatch):
    """Try building a flask app obj without the env variable being set"""
    _LOGGER.info("Begin test")

    # expected config settings
    expected_config_settings = {
        'DEBUGGING': False,
        'SECRET_KEY': 'unit-test-super-secret-key',
    }

    # create a temp file with the test config
    config_file = tempfile.NamedTemporaryFile()
    for key, value in expected_config_settings.items():
        if isinstance(value, str):
            output_value = '{} = "{}"\n'.format(key, value)
        else:
            output_value = '{} = {}\n'.format(key, value)
        # kludge to make this py2+3 compatible on the cheap
        config_file.write(output_value.encode('utf-8'))
    config_file.flush()

    # add a custom env variable setting
    _LOGGER.debug("Patching env with %s set to '%s'", my_factory.FLASK_CONFIG_PATH_ENV_VAR,
                  config_file.name)
    monkeypatch.setenv(my_factory.FLASK_CONFIG_PATH_ENV_VAR, config_file.name)

    # now run the factory
    app = my_factory.build_app()
    assert app
    for key, expected_value in expected_config_settings.items():
        assert app.config[key] == expected_value

    # clean up if test passes this far
    os.unlink(config_file.name)

    _LOGGER.info("Finished test")
