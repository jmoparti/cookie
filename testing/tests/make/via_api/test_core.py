# -*- coding: utf-8 -*-
"""
Test suites for core test scenarios with make targets in emitted templates on local host via
Cookiecutter's Python API.
"""

#
# Imports
#

# import core
import copy
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
from tests.make.common.make_utils import MakeTargetPermutationBuilder
from tests.make.common.misc_utils import (
    SpecificTestParams,
)

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)

# pytest markers
pytestmark = [pytest.mark.custom_make_test, pytest.mark.custom_api_test]


#
# Tests
#

def pytest_generate_tests(metafunc):
    """Metafunc hook for generating parameters for make tests"""
    _LOGGER.debug("Begin generating test params using metafunc")

    # bail out if you're not trying to use specific_test_params
    if 'specific_test_params' not in metafunc.funcargnames:
        # skip this test function
        return

    # get the test function name
    test_function_name = metafunc.function.__name__
    _LOGGER.debug("metafunc test function is named: %s", test_function_name)

    # given the test function name, pick some baseline variables
    list_of_specific_params = []
    permutation_builder = MakeTargetPermutationBuilder()
    if test_function_name == 'test_defaults':
        # Try every project flavor with every python version mode and the default dependency
        # management mode
        for project_flavor in ProjectFlavor:
            for python_version_mode in PythonVersionMode:
                for dependency_management_mode in [next(iter(DependencyManagementMode))]:
                    specific_params = SpecificTestParams(
                        dependency_management_mode=dependency_management_mode,
                        make_targets=[],
                        project_flavor=project_flavor,
                        python_version_mode=python_version_mode,
                    )
                    list_of_specific_params.append(specific_params)

        # Try the default project flavor with the default python version and with every
        # dependency management mode.
        for project_flavor in [next(iter(ProjectFlavor))]:
            for python_version_mode in [next(iter(PythonVersionMode))]:
                for dependency_management_mode in DependencyManagementMode:
                    specific_params = SpecificTestParams(
                        dependency_management_mode=dependency_management_mode,
                        make_targets=[],
                        project_flavor=project_flavor,
                        python_version_mode=python_version_mode,
                    )
                    list_of_specific_params.append(specific_params)

    elif test_function_name == 'test_non_defaults':
        # Exercise the non-default make targets with the library flavor because it has
        # just enough meat on its bones to try out the stuff

        project_flavor = ProjectFlavor.LIBRARY
        python_version_mode = next(iter(PythonVersionMode))
        dependency_management_mode = next(iter(DependencyManagementMode))
        non_default_make_targets = permutation_builder.get_targets_not_called_by_default()

        for make_target in non_default_make_targets:
            specific_params = SpecificTestParams(
                dependency_management_mode=dependency_management_mode,
                make_targets=[make_target],
                project_flavor=project_flavor,
                python_version_mode=python_version_mode,
            )
            list_of_specific_params.append(specific_params)
    else:
        # bail out if your test function is not supported
        return

    _LOGGER.debug("Now generate the test parameters")
    data = GeneratorForPytestParameterization.from_specific_test_params(
        list_of_specific_params)
    _LOGGER.debug("Generated %d combinations", len(data['arg_values']))

    # return via hook
    metafunc.parametrize(
        data['arg_names'],
        data['arg_values'],
        indirect=False,
        ids=data['arg_ids'],
        scope=None)
    _LOGGER.debug("Finished generating test params using metafunc")


def test_defaults(basic_test_params, specific_test_params, specific_test_params_filter):
    """Test default make targets via the cookiecutter api"""

    func_params = locals()
    _LOGGER.debug("Begin invoking test with %s", str(func_params))
    run_api_test(basic_test_params, specific_test_params, specific_test_params_filter)
    _LOGGER.debug("Finished invoking test with %s", str(func_params))


def test_non_defaults(basic_test_params, specific_test_params, specific_test_params_filter):
    """Test non-default make targets via the cookiecutter api"""

    func_params = locals()
    _LOGGER.debug("Begin invoking test with %s", str(func_params))
    run_api_test(basic_test_params, specific_test_params, specific_test_params_filter)
    _LOGGER.debug("Finished invoking test with %s", str(func_params))
