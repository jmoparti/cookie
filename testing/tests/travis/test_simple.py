# -*- coding: utf-8 -*-
"""
Test travis wiring in emitted projects.
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
    PythonVersionMode,
)
from tests.travis.common import (
    SpecificTestParams,
    convert_specific_params_to_metafunc_arg_id,
    mint_extra_context,
)
from tests.common.cookiecutter_utils import (
    CookieCutterInvoker,
)
from tests.common.git_utils import (
    prepare_minimal_viable_git_repo,
)
from tests.common.output_utils import (
    OutputDirectoryManager,
)

from tests.common.assertion_utils import (
    TravisFileSpec,
)

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)

# pytest marker
pytestmark = [pytest.mark.custom_travis_test]


#
# Pytest hooks
#

def pytest_generate_tests(metafunc):
    """Metafunc hook for generating parameters for travis tests"""

    # bail out if you're not trying to use specific_test_params
    if 'specific_test_params' not in metafunc.funcargnames:
        return

    # generate all the combos
    arg_names = 'specific_test_params'
    arg_ids = []
    arg_values = []
    for python_version_mode in iter(PythonVersionMode):
        for dependency_management_mode in iter(DependencyManagementMode):
            combo = SpecificTestParams(
                dependency_management_mode=dependency_management_mode,
                python_version_mode=python_version_mode,
            )
            arg_id = convert_specific_params_to_metafunc_arg_id(combo)
            arg_ids.append(arg_id)
            arg_values.append(combo)

    # return via hook
    metafunc.parametrize(arg_names, arg_values, indirect=False, ids=arg_ids, scope=None)


#
# Tests
#

def test_travis_build(basic_test_params, specific_test_params):
    func_params = locals()
    _LOGGER.debug("Begin invoking test with %s", func_params)

    # mint a default context
    extra_context = mint_extra_context(
        basic_test_params.cookiecutter_json_data, specific_test_params)

    # setup output directory
    output_dir_manager = OutputDirectoryManager(
        basic_test_params=basic_test_params,
        specific_test_params=specific_test_params,
        prefix="travis")
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

    # do basic validation on the travis files
    travis_file_spec = TravisFileSpec(project_output_path)
    travis_file_spec.assert_dot_travis_yml(
        specific_test_params.dependency_management_mode, specific_test_params.python_version_mode)

    # setup that output project as a minimally viable git repo
    prepare_minimal_viable_git_repo(project_output_path)

    # TODO - the rest of this testing is sadly manual
    _LOGGER.warning("Ok, now you have to do manual testing with EC travis using the emitted templates :(")

    _LOGGER.debug("Finished invoking test with %s", func_params)
