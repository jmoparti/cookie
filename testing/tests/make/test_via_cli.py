# -*- coding: utf-8 -*-
"""
Test make targets in emitted template on local host via Cookiecutter's command line.
"""
#
# Imports
#

# import core
import logging
import os

# import third party
import pytest

# this project
from tests.constants import (
    DependencyManagementMode,
    MakeTarget,
    ProjectFlavor,
    PythonVersionMode,
)

from tests.common.cookiecutter_utils import (
    CookieCutterInvoker,
)
from tests.common.output_utils import (
    OutputDirectoryManager,
)
from tests.make.common.cookiecutter_utils import (
    mint_extra_context,
)
from tests.make.common.make_utils import (
    run_make_on_host,
)
from tests.make.common.misc_utils import (
    SpecificTestParams,
)
from tests.make.common.pytest_utils import (
    GeneratorForPytestParameterization,
    skip_if_missing_an_intrepreter,
    skip_if_not_cookiecutter_defaults,
)
from tests.make.common.assertion_utils import (
    assert_expected_files,
)

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)


# pytest markers
pytestmark = [pytest.mark.custom_make_test, pytest.mark.custom_cli_test]


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
    if test_function_name == 'test_via_cli':
        # Exercise the default make targets for all combinations of project
        # flavors, dependency modes and python versions
        for python_version_mode in PythonVersionMode:
            for dependency_management_mode in DependencyManagementMode:
                for project_flavor in ProjectFlavor:
                    specific_params = SpecificTestParams(
                        dependency_management_mode=dependency_management_mode,
                        make_targets=[],
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
    metafunc.parametrize(data['arg_names'], data['arg_values'],
                         indirect=False, ids=data['arg_ids'], scope=None)

    _LOGGER.debug("Finished generating test params using metafunc")


def test_via_cli(basic_test_params, specific_test_params):
    func_params = locals()
    _LOGGER.debug("Begin invoking test with %s", func_params)
    assert isinstance(specific_test_params, SpecificTestParams)

    # first see if should skip this combo of params because they aren't the defaults in
    # cookiecutter.json
    skip_if_not_cookiecutter_defaults(basic_test_params, specific_test_params)

    # skip if you're missing the interpreter
    skip_if_missing_an_intrepreter(specific_test_params)

    # mint a default context
    extra_context = mint_extra_context(
        basic_test_params.cookiecutter_json_data, specific_test_params)

    # generate a parameterized sub-dir in the root output directory
    output_dir_manager = OutputDirectoryManager(
        basic_test_params=basic_test_params,
        specific_test_params=specific_test_params,
        prefix="cli")
    test_output_path = output_dir_manager.setup()

    # call cookiecutter CLI
    invoker = CookieCutterInvoker(
        repo_root_path=basic_test_params.repo_root_path,
        cookiecutter_config_path=basic_test_params.cookiecutter_config_path)
    invoker.invoke_via_cli(
        working_path=os.path.abspath(os.getcwd()),
        root_output_path=test_output_path)

    # figure out where the test output_path should have ended up
    project_output_path = output_dir_manager.get_project_output_path()

    # do rudimentary file checks
    assert_expected_files(basic_test_params, specific_test_params, project_output_path)

    # run make in the project that was emitted
    run_make_on_host(specific_test_params, project_output_path)

    # done with test
    _LOGGER.debug("Finished invoking test with %s", func_params)
