# -*- coding: utf-8 -*-
"""
Test vagrant 'build_vm' in the emitted template
"""


#
# Imports
#

# import core
import logging

# import third party
import pytest

from tests.common.cookiecutter_utils import (
    CookieCutterInvoker,
)
from tests.common.git_utils import (
    prepare_minimal_viable_git_repo,
)
from tests.common.output_utils import (
    OutputDirectoryManager,
)
# this project
from tests.constants import (
    PythonRepoMode,
    PythonVersionMode,
    VagrantBoxMode,
    VagrantVM,
    VagrantVMRole,
)
from tests.vagrant.common.cookiecutter_utils import (
    mint_extra_context,
)
from tests.vagrant.common.misc_utils import (
    SpecificTestParams,
)
from tests.vagrant.common.pytest_utils import (
    convert_specific_params_to_metafunc_arg_id,
    skip_if_no_vagrant_executable,
)
from tests.vagrant.common.vagrant_utils import (
    invoke_vagrant_command,
)

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)

# pytest marker
pytestmark = [pytest.mark.custom_vagrant_test, pytest.mark.custom_build_vm_test]


#
# Pytest hooks
#

def pytest_generate_tests(metafunc):
    """Metafunc hook for generating parameters for vagrant build vm tests"""

    # bail out if you're not trying to use specific_test_params
    if 'specific_test_params' not in metafunc.funcargnames:
        return

    # pick a vm list based on test scenario
    if metafunc.function.__name__ == 'test_make_in_vm':
        vagrant_vms = []
        for vagrant_vm in iter(VagrantVM):
            if vagrant_vm.vm_role == VagrantVMRole.BUILD:
                vagrant_vms.append(vagrant_vm)
        if not vagrant_vms:
            return
    else:
        return

    # pick vagrant box modes
    vagrant_box_modes = iter(VagrantBoxMode)

    # pick python version modes
    python_version_modes = iter(PythonVersionMode)

    # pick repo modes
    python_repo_modes = [PythonRepoMode.PUBLIC_ONLY]

    # generate all the combos
    arg_names = 'specific_test_params'
    arg_ids = []
    arg_values = []
    for vagrant_vm in vagrant_vms:
        for vagrant_box_mode in vagrant_box_modes:
            for python_version_mode in python_version_modes:
                for python_repo_mode in python_repo_modes:
                    combo = SpecificTestParams(
                        python_repo_mode=python_repo_mode,
                        python_version_mode=python_version_mode,
                        vagrant_vm=vagrant_vm,
                        vagrant_box_mode=vagrant_box_mode,
                    )
                    arg_id = convert_specific_params_to_metafunc_arg_id(combo)
                    arg_ids.append(arg_id)
                    arg_values.append(combo)

    # return via hook
    metafunc.parametrize(arg_names, arg_values, indirect=False, ids=arg_ids, scope=None)


#
# Tests
#

def test_make_in_vm(basic_test_params, specific_test_params):
    func_params = locals()
    _LOGGER.debug("Begin invoking test with %s", func_params)

    # skip if no vagrant exe
    skip_if_no_vagrant_executable()

    # check vm
    vagrant_vm = specific_test_params.vagrant_vm
    if vagrant_vm.vm_role != VagrantVMRole.BUILD:
        pytest.skip("Vagrant VM {} not in role {}".format(vagrant_vm.vm_name, VagrantVMRole.BUILD))

    # mint a default context
    extra_context = mint_extra_context(
        basic_test_params.cookiecutter_json_data, specific_test_params)

    # setup output directory
    output_dir_manager = OutputDirectoryManager(
        basic_test_params=basic_test_params,
        specific_test_params=specific_test_params,
        prefix="build")
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

    # setup that output project as a minimally viable git repo
    prepare_minimal_viable_git_repo(project_output_path)

    # run a test within the vagrant vm
    try:
        invoke_vagrant_command(project_output_path, [
            vagrant_vm.get_status_cmd(),
            vagrant_vm.get_destroy_cmd(),
            vagrant_vm.get_up_cmd(),
            vagrant_vm.get_ssh_cmd('cd ~/cleanroom && make'),
        ])
    except Exception as error:
        _LOGGER.exception(
            "Fatal error while running ssh commands within vm under test %s",
            specific_test_params.vagrant_vm)
        pytest.fail("Action within vagrant vm {} failed, see logs for details: {}".format(
            specific_test_params.vagrant_vm.name, error))
    finally:
        _LOGGER.debug("tear down vagrant vm under test")
        invoke_vagrant_command(project_output_path, [vagrant_vm.get_destroy_cmd()])

    # done with test
    _LOGGER.debug("Finished invoking test with %s", func_params)
