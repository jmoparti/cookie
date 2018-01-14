"""
Pytest configuration fixtures and hooks
"""

#
# Imports
#

# core python
import logging

# third party

# this project
from tests.constants import (
    DependencyManagementMode,
    MakeTarget,
    ProjectFlavor,
    PythonVersionMode,
)

# import to expose to pytest magic
from tests.fixtures import (
    basic_test_params,
    cookiecutter_config_path,
    cookiecutter_json_data,
    cookiecutter_json_path,
    original_cookiecutter_json_data,
    repo_root_path,
    root_output_path,
    specific_test_params_filter,
)

#
# Module stuff
#

# instantiate logger
_LOGGER = logging.getLogger(__name__)

#
# Hooks
#


def pytest_addoption(parser):
    """Add custom pytest command line options"""

    parser.addoption(
        "--only-dependency-management-mode",
        choices=[item.name.lower() for item in DependencyManagementMode],
        type=str,
        help="Override dependency management mode used in tests")

    parser.addoption(
        "--only-make-target",
        choices=[item.name.lower() for item in MakeTarget],
        type=str,
        help="Override the make targets used in tests")

    parser.addoption(
        "--only-project-flavor",
        choices=[item.name.lower() for item in ProjectFlavor],
        type=str,
        help="Override project flavor used in tests")

    parser.addoption(
        "--only-python-version-mode",
        choices=[item.name.lower() for item in PythonVersionMode],
        type=str,
        help="Override python version mode used in tests")

    parser.addoption(
        "--retain-passed-test-data",
        action="store_true",
        default=False,
        help="Retain data from successful tests")
