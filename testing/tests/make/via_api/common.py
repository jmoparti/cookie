# -*- coding: utf-8 -*-
"""
Re-usable code for testing makefile via cookiecutter api calls
"""

#
# Imports
#

# import core
import logging

# import third party

# this project
from tests.fixtures import (
    BasicTestParams,
    SpecificTestParamsFilter,
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
    skip_if_missing_an_intrepreter,
    skip_if_no_match_for_specific_params_filter,
)
from tests.make.common.assertion_utils import (
    assert_expected_files,
    assert_expected_makefile,
    assert_expected_wheel_is_built,
)
from tests.constants import (
    MakeTarget,
)

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)


#
# Functions
#

def run_api_test(basic_test_params, specific_test_params, specific_test_params_filter):
    """Re-usable underlying implementation for running tests via the cookiecutter Python API"""
    func_params = locals()
    _LOGGER.debug("Begin with %s", func_params)
    assert isinstance(basic_test_params, BasicTestParams)
    assert isinstance(specific_test_params, SpecificTestParams)
    assert isinstance(specific_test_params_filter, SpecificTestParamsFilter)

    # skip if you're missing the interpreter
    skip_if_missing_an_intrepreter(specific_test_params)

    # skip if the current specific test params don't match the filter (if any)
    skip_if_no_match_for_specific_params_filter(specific_test_params, specific_test_params_filter)

    # mint a default context
    extra_context = mint_extra_context(
        basic_test_params.cookiecutter_json_data, specific_test_params)

    # generate a parameterized sub-dir in the root output directory
    output_dir_manager = OutputDirectoryManager(
        basic_test_params=basic_test_params,
        specific_test_params=specific_test_params,
        prefix="api")
    test_output_path = output_dir_manager.setup()

    # call cookiecutter python API entry point (same one used by cli)
    invoker = CookieCutterInvoker(
        repo_root_path=basic_test_params.repo_root_path,
        cookiecutter_config_path=basic_test_params.cookiecutter_config_path)
    invoker.invoke_via_api(
        root_output_path=test_output_path,
        extra_context=extra_context)

    # figure out where the test output_path should have ended up
    project_output_path = output_dir_manager.get_project_output_path()

    # do rudimentary file checks
    assert_expected_files(basic_test_params, specific_test_params, project_output_path)

    # assert the expected makefile is there
    assert_expected_makefile(basic_test_params, specific_test_params, project_output_path)

    # run make in the project that was emitted
    run_make_on_host(specific_test_params, project_output_path)

    # the make targets were supposed to build a wheel, then assert the built wheel is right
    if not specific_test_params.make_targets or \
            MakeTarget.should_build_a_wheel(*specific_test_params.make_targets):
        _LOGGER.debug(
            "Trying to check wheel metadata since make targets indicate that it should build one")
        assert_expected_wheel_is_built(basic_test_params, specific_test_params, project_output_path)
    else:
        _LOGGER.debug("Skipping wheel check because make targets should not result in a wheel: %s",
                      str(specific_test_params.make_targets))

    # if test passed, and retain-data flag is false, then remove the project_output_path
    if basic_test_params.retain_passed_test_data:
        _LOGGER.debug("Retaining data from passing test: %s", project_output_path)
    else:
        _LOGGER.debug("Removing data from passing test: %s", project_output_path)
        output_dir_manager.tear_down()

    # done with test
    _LOGGER.debug("Finished with %s", func_params)
