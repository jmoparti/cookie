# -*- coding: utf-8 -*-
"""
Utilities for test assertions specific to tests specific to makefile targets
"""

#
# Imports
#

# import core
import glob
import logging
import os
import pprint
import stat

# import third party
import testfixtures

# this project
from tests.fixtures import (
    BasicTestParams,
)

from tests.constants import (
    MakeTarget,
)
from tests.common.cookiecutter_utils import (
    CookiecutterJSONField,
)
from tests.make.common.cookiecutter_utils import (
    mint_extra_context,
)
from tests.make.common.misc_utils import (
    SpecificTestParams,
)
from tests.common.assertion_utils import (
    FileSystemSpec,
    PythonPackageSpec,
    PipRequirementsFileSpec,
    TravisFileSpec,
)
from tests.make.common.make_utils import (
    parse_makefile,
)

# logger
_LOGGER = logging.getLogger(__name__)


#
# Helper stuff
#


def assert_expected_files(basic_test_params, specific_test_params, project_output_path):
    """Assert that the expected file structure was emitted"""
    func_params = locals()
    _LOGGER.debug("Begin asserting that the expected files were emitted for: %s",
                  str(func_params))

    # error check inputs
    assert isinstance(basic_test_params, BasicTestParams)
    assert isinstance(specific_test_params, SpecificTestParams)

    # build the extra context
    cookiecutter_extra_context = mint_extra_context(
        basic_test_params.cookiecutter_json_data,
        specific_test_params)

    # setup file system spec
    file_system_spec = FileSystemSpec(
        root_origin_directory=basic_test_params.repo_root_path,
        root_target_directory=project_output_path,
        cookiecutter_extra_context=cookiecutter_extra_context)
    _LOGGER.debug("current file system spec before updating:\n%s", pprint.pformat(file_system_spec))

    # update with file system specs based on the test parameters
    file_system_spec.specify_by_project_flavor(specific_test_params.project_flavor)
    file_system_spec.specify_by_python_version_mode(specific_test_params.python_version_mode)

    # update file modes for stuff common to all variations
    files_to_check_perms_for = {
        'vagrant/install-basic-python.sh': [stat.S_IXUSR],
        'vagrant/make-cleanroom-copy-of-repo.sh': [stat.S_IXUSR],
        'vagrant/provision-build-vm.sh': [stat.S_IXUSR],
    }
    for relative_path, stat_bit_masks in files_to_check_perms_for.items():
        file_system_spec.specify_file_mode(relative_path, stat_bit_masks)

    # now do all the file system spec assertions
    _LOGGER.debug("Expected file system specification is:\n%s", pprint.pformat(file_system_spec))
    file_system_spec.assert_all()

    # make sure the requirements text files are parse-able
    pip_req_file_spec = PipRequirementsFileSpec(project_output_path)
    pip_req_file_spec.assert_requirements_files()

    # make sure the .travis.yml text files are parse-able
    travis_file_spec = TravisFileSpec(project_output_path)
    travis_file_spec.assert_dot_travis_yml(
        specific_test_params.dependency_management_mode, specific_test_params.python_version_mode)

    _LOGGER.debug("Finished asserting that the expected files were emitted for: %s",
                  str(func_params))


def assert_expected_makefile(basic_test_params, specific_test_params, project_output_path):
    """Assert that the expected file structure was emitted"""
    func_params = locals()
    _LOGGER.debug("Begin asserting that the expected Makefile was emitted for: %s",
                  str(func_params))

    # error check inputs
    assert isinstance(basic_test_params, BasicTestParams)
    assert isinstance(specific_test_params, SpecificTestParams)

    # build the extra context
    cookiecutter_extra_context = mint_extra_context(
        basic_test_params.cookiecutter_json_data,
        specific_test_params)

    # parse the makefile
    parsed_makefile = parse_makefile(project_output_path)
    found_target_names = set(parsed_makefile['targets'])

    # marshal a set of expected target names
    expected_target_names = set()
    for expected_make_target in MakeTarget:
        assert isinstance(expected_make_target, MakeTarget)
        expected_target_names.add(expected_make_target.target_name)

    # compare found target names to expected
    testfixtures.compare(found_target_names, expected_target_names)

    _LOGGER.debug("Finished asserting that the expected Makefile was emitted for: %s",
                  str(func_params))


def assert_expected_wheel_is_built(basic_test_params, specific_test_params, project_output_path):
    """Assert that the expected wheel can be built with the emitted template"""
    func_params = locals()
    _LOGGER.debug(
        "Begin asserting the expected wheel was built with the template emitted for %s",
        str(func_params))

    # error check inputs
    assert isinstance(basic_test_params, BasicTestParams)
    assert isinstance(specific_test_params, SpecificTestParams)

    # setup the spec for the python package itself
    py_pkg_spec = PythonPackageSpec(
        basic_test_params.cookiecutter_json_data, specific_test_params, project_output_path)

    # iterate across all package formats you care about
    dist_path = os.path.join(project_output_path)
    glob_pattern = "{}/dist/*.whl".format(dist_path)

    found_at_least_one_package = False
    for globbed_path in glob.glob(glob_pattern):
        found_at_least_one_package = True
        py_pkg_spec.assert_basic_meta_data(package_path=globbed_path)
        py_pkg_spec.assert_package_contents(package_path=globbed_path)

    # make sure you found at least one package
    assert found_at_least_one_package, \
        "Did not find any Python package files for glob pattern '{}'".format(glob_pattern)

    _LOGGER.debug(
        "Finished asserting the expected wheel was built with the template emitted for %s",
        str(func_params))
