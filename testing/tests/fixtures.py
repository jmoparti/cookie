# -*- coding: utf-8 -*-
"""
Common fixtures
"""

#
# Imports
#

# import core
import copy
import json
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
    CookiecutterJSONSchema,
)
from tests.common.misc_utils import (
    BasicTestParams,
    SpecificTestParamsFilter,
)

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)


#
# Fixtures
#

@pytest.fixture(scope="session")
def repo_root_path():
    """Path to the project's repo root directory"""
    return os.path.abspath('..')


@pytest.fixture(scope="session")
def cookiecutter_json_path(repo_root_path):
    """JSON data ready from the template's default cookiecutter.json"""
    path = os.path.join(repo_root_path, 'cookiecutter.json')
    assert os.path.exists(path), "Path {} does not exist".format(path)
    return path


@pytest.fixture(scope="session")
def original_cookiecutter_json_data(cookiecutter_json_path):
    """Original copy of JSON data read from the template's default cookiecutter.json"""
    with open(cookiecutter_json_path, 'r') as json_file:
        json_data = json.load(json_file)
    _LOGGER.debug("Read this json from %s : %s", cookiecutter_json_path, json_data)
    CookiecutterJSONSchema.raise_if_invalid(json_data)
    _LOGGER.debug("JSON passes validation against schema")
    return json_data


@pytest.fixture(scope="session")
def root_output_path(repo_root_path):
    """Path to the root output directory that cookiecutter will write to"""
    root_output_path = os.path.join(repo_root_path, 'testing', 'output')
    if not os.path.exists(root_output_path):
        os.mkdir(root_output_path)
    return root_output_path


@pytest.fixture(scope="session")
def cookiecutter_config_path():
    """Path to the cookiecutter yaml config file to use"""
    return os.path.abspath(os.path.join('.', 'cookiecutter-config.yaml'))


@pytest.fixture(scope="session")
def specific_test_params_filter(request):
    """Setup optional filter for specific test params"""
    kwarg_to_option_name_map = {
        "dependency_management_mode": "only_dependency_management_mode",
        "make_targets": "only_make_target",
        "project_flavor": "only_project_flavor",
        "python_version_mode": "only_python_version_mode",
    }
    option_name_to_enum_map = {
        "only_dependency_management_mode": DependencyManagementMode,
        "only_make_target": MakeTarget,
        "only_project_flavor": ProjectFlavor,
        "only_python_version_mode": PythonVersionMode,
    }
    kwargs = {}
    for kwarg_name, option_name in kwarg_to_option_name_map.items():
        enum_class = option_name_to_enum_map[option_name]
        option_value = request.config.getoption(option_name, default=None, skip=False)
        if option_value is not None:
            enum_value = enum_class[option_value.upper()]
            if kwarg_name == 'mark_targets':
                kwarg_value = [enum_value]
            else:
                kwarg_value = enum_value
        else:
            kwarg_value = None
        kwargs[kwarg_name] = kwarg_value
    return SpecificTestParamsFilter(**kwargs)


@pytest.fixture(scope="function")
def cookiecutter_json_data(original_cookiecutter_json_data):
    """Isolated copy of original cookiecutter.json data"""
    return copy.deepcopy(original_cookiecutter_json_data)


@pytest.fixture(scope="function")
def basic_test_params(
    pytestconfig,
    repo_root_path,
    cookiecutter_config_path,
    cookiecutter_json_data,
    root_output_path):
    """Group of basic parameters for conducting a test of the emitted project's make targets"""
    retain_passed_test_data = pytestconfig.getoption(
        'retain_passed_test_data', default=False, skip=False)
    data = BasicTestParams(
        repo_root_path=repo_root_path,
        cookiecutter_config_path=cookiecutter_config_path,
        cookiecutter_json_data=cookiecutter_json_data,
        root_output_path=root_output_path,
        retain_passed_test_data=retain_passed_test_data)
    _LOGGER.debug("Created these basic test params: %s", data)
    return data
