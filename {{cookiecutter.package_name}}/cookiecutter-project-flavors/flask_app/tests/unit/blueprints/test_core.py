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

@pytest.mark.parametrize('test_url,expected_status_code', [
    ('/', 200),
    ('/index.html', 200)
])
def test_getting_index(unset_env_variables, test_url, expected_status_code):
    _LOGGER.info("Begin test")

    # Make sure the env variable is NOT set
    assert os.getenv(my_factory.FLASK_CONFIG_PATH_ENV_VAR, None) is None

    # now run the factory
    app = my_factory.build_app()
    assert app

    # try the test client
    test_client = app.test_client()
    result = test_client.get(test_url)
    _LOGGER.debug("Got index from %s: %s", test_url, result)
    assert result.status_code == expected_status_code

    _LOGGER.info("Finished test")
