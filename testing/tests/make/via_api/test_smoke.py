# -*- coding: utf-8 -*-
"""
Smoke test suites for make targets in emitted template on local host via Cookiecutter's Python API.
"""

#
# Imports
#

# import core
import logging

# import third party
import pytest

# this project
from tests.constants import (
    DependencyManagementMode,
    MakeTarget,
    ProjectFlavor,
    PythonVersionMode,
)
from tests.make.common.pytest_utils import (
    GeneratorForPytestParameterization,
)
from tests.make.via_api.common import run_api_test

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)

# pytest markers
pytestmark = [
    pytest.mark.custom_smoke_test,
    pytest.mark.custom_make_test,
    pytest.mark.custom_api_test]


#
# Tests
#

def pytest_generate_tests(metafunc):
    """Metafunc hook for generating parameters for make tests"""
    _LOGGER.debug("Begin generating test params using metafunc")

    #
    # bail out if you're not trying to use specific_test_params
    #

    if 'specific_test_params' not in metafunc.funcargnames:
        # skip this test function
        return

    #
    # get the test function name
    #
    test_function_name = metafunc.function.__name__
    _LOGGER.debug("metafunc test function is named: %s", test_function_name)

    #
    # given the test function name, pick some baseline variables
    #

    if test_function_name == 'test_via_api':
        # set basic kwargs
        kwargs_for_param_generator = {
            'dependency_management_modes': [next(iter(DependencyManagementMode))],
            'project_flavors': [next(iter(ProjectFlavor))],
            'python_version_modes':  [next(iter(PythonVersionMode))],
            'make_target_lists': [[]], # use default make target list
        }
    else:
        # bail out if your test function is not supported
        return

    _LOGGER.debug("Now generate the test parameters")
    data = GeneratorForPytestParameterization.from_combinations_of_cookiecutter_params(
        **kwargs_for_param_generator)
    _LOGGER.debug("Generated %d combinations", len(data['arg_values']))

    # return via hook
    metafunc.parametrize(
        data['arg_names'],
        data['arg_values'],
        indirect=False,
        ids=data['arg_ids'],
        scope=None)
    _LOGGER.debug("Finished generating test params using metafunc")


def test_via_api(basic_test_params, specific_test_params, specific_test_params_filter):
    func_params = locals()
    _LOGGER.debug("Begin invoking test with %s", str(func_params))
    run_api_test(basic_test_params, specific_test_params, specific_test_params_filter)
    _LOGGER.debug("Finished invoking test with %s", str(func_params))
