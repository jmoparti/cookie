# -*- coding: utf-8 -*-
"""
Utilities related to pytest plumbing specific to tests specific to makefile targets
"""

#
# Imports
#

# import core
import logging
import pprint

# import third party
import pytest

# this project
from tests.constants import (
    DependencyManagementMode,
    MakeTarget,
    ProjectFlavor,
    PythonVersionMode,
)
from tests.fixtures import (
    BasicTestParams,
    SpecificTestParamsFilter,
)
from tests.common.cookiecutter_utils import (
    CookiecutterJSONField,
)
import tests.common.pytest_utils
import tests.common.output_utils
from tests.make.common.cookiecutter_utils import (
    mint_extra_context
)
from tests.make.common.misc_utils import (
    SpecificTestParams,
)

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)


#
# Functions
#

def skip_if_missing_an_intrepreter(specific_test_params):
    # skip if you're missing the interpreter
    assert isinstance(specific_test_params, SpecificTestParams)
    for python_version in specific_test_params.python_version_mode.python_versions:
        tests.common.pytest_utils.skip_if_missing_python_interpreter(python_version)


def skip_if_no_match_for_specific_params_filter(specific_test_params, specific_test_params_filter):
    """Skip test if the specific test params don't match the filter"""
    _LOGGER.debug("Comparing actual specific test params %s to the filter %s", specific_test_params,
                  specific_test_params_filter)
    assert isinstance(specific_test_params, SpecificTestParams)
    assert isinstance(specific_test_params_filter, SpecificTestParamsFilter)

    # describe what kind of value is being filtered
    filter_config = {
        'dependency_management_mode': 'single_value',
        'make_targets': 'list_of_values',
        'project_flavor': 'single_value',
        'python_version_mode': 'single_value',
    }
    for filter_attr_name, type_of_filtered_value in filter_config.items():
        _LOGGER.debug("Checking filter attribute %s with %s type of filtered value",
                      filter_attr_name, type_of_filtered_value)
        filter_attr_value = getattr(specific_test_params_filter, filter_attr_name)
        _LOGGER.debug("Checking versus filter attribute value %s", filter_attr_value)
        if filter_attr_value is not None:
            actual_attr_value = getattr(specific_test_params, filter_attr_name)
            _LOGGER.debug("Actual attr value %s", actual_attr_value)

            # compare to filter
            matches_filter = False
            if type_of_filtered_value == 'single_value':
                matches_filter = (actual_attr_value == filter_attr_value)
            elif type_of_filtered_value == 'list_of_values':
                matches_filter = (filter_attr_value in actual_attr_value)
            else:
                raise Exception("Unsupported type of filtered value: '%s'", type_of_filtered_value)

            # now log or skip
            if matches_filter:
                _LOGGER.debug(
                    "Value for field %s of specific test params has value %s which does match "
                    "the filter criteria: %s", filter_attr_name, actual_attr_value,
                    filter_attr_value)
            else:
                message = (
                    "Value for field {} of specific test params has value {} which does not match "
                    "the filter criteria: {}").format(
                    filter_attr_name, actual_attr_value, filter_attr_value)
                pytest.skip(message)


def skip_if_not_cookiecutter_defaults(basic_test_params, specific_test_params):
    """If the specific test params don't match the defaults in cookiecutter.json, skip the test"""
    assert isinstance(basic_test_params, BasicTestParams)
    assert isinstance(specific_test_params, SpecificTestParams)

    # build an extra context
    extra_context = mint_extra_context(
        basic_test_params.cookiecutter_json_data, specific_test_params)

    # pick which json fields to care about non-default or not
    for field_enum in tuple(CookiecutterJSONField):
        if field_enum.choices_enum:
            default_value = field_enum.get_available_choices()[0]
            field_name = field_enum.json_name
            actual_value = extra_context[field_name]
            if actual_value != default_value:
                pytest.skip(
                    "Value for cookiecutter 'extra context' field {} , '{}, does not match "
                    "the default value: '{}'".format(field_name, actual_value, default_value))


class GeneratorForPytestParameterization(object):
    """
    Generator for parameters for pytest parameterization of make related tests
    """

    @staticmethod
    def _convert_specific_params_to_metafunc_arg_id(specific_test_params):
        """
        convert the values of the specific test params tuple into printable arg id
        for pytest test parameterization
        """
        assert isinstance(specific_test_params, tests.make.common.misc_utils.SpecificTestParams)
        params_hash = tests.common.output_utils.OutputDirectoryManager.build_params_hash(
            specific_test_params)

        if specific_test_params.make_targets:
            make_targets_id_str = "make-{}".format(','.join(
                MakeTarget.format_for_make(specific_test_params.make_targets)))
        else:
            make_targets_id_str = 'make-DEFAULT_MAKE_TARGET'
        arg_id = '-'.join([
            specific_test_params.python_version_mode.name.lower(),
            specific_test_params.dependency_management_mode.name.lower(),
            specific_test_params.project_flavor.name.lower(),
            make_targets_id_str,
            params_hash,
        ])
        return arg_id

    @staticmethod
    def from_specific_test_params(list_of_specific_test_params):
        """
        Generate a set of pytest params from specific test params
        for use by metafunc injection in conftest.py files.
        """
        _LOGGER.debug("Begin generating a set of pytest params from specific test params")

        # generate the combos of parameters
        generated_params = {
            'arg_names': 'specific_test_params',
            'arg_ids': [],
            'arg_values': [],
        }
        for specific_test_params in list_of_specific_test_params:
            assert isinstance(specific_test_params, SpecificTestParams)
            arg_id = GeneratorForPytestParameterization._convert_specific_params_to_metafunc_arg_id(
                specific_test_params)
            generated_params['arg_ids'].append(arg_id)
            generated_params['arg_values'].append(specific_test_params)

        _LOGGER.debug("Generated these pytest parameters:\n%s", pprint.pformat(generated_params))

        _LOGGER.debug("Finished generating a set of pytest params from specific test params")
        return generated_params

    @staticmethod
    def from_combinations_of_cookiecutter_params(
            python_version_modes=None,
            dependency_management_modes=None,
            project_flavors=None,
            make_target_lists=None):
        """
        Generate pytest parameter sets based on combinations of cookiecutter parameters
        and make file targets.
        """

        _LOGGER.debug("Begin generating basic combos of test parameters")
        _LOGGER.debug("Using these inputs:\n%s", pprint.pformat({
            'python_version_mode': python_version_modes,
            'dependency_management_modes': dependency_management_modes,
            'project_flavors': project_flavors,
            'make_target_lists': make_target_lists,
        }))

        # set sane defaults (to first of the possible options or just empty list)
        if not dependency_management_modes:
            dependency_management_modes = [next(iter(DependencyManagementMode))]
        if not project_flavors:
            project_flavors = [next(iter(ProjectFlavor))]
        if not python_version_modes:
            python_version_modes = [next(iter(PythonVersionMode))]
        if not make_target_lists:
            # use a list of one kind of make targets list, and make that an empty list
            # this will tell the underlying test runner to call make without stipulating a make
            # target
            make_target_lists = [[]]

        # generate the combos of parameters
        list_of_specific_test_params = []
        for python_version_mode in python_version_modes:
            for dependency_management_mode in dependency_management_modes:
                for project_flavor in project_flavors:
                    for make_targets in make_target_lists:
                        combo = SpecificTestParams(
                            dependency_management_mode=dependency_management_mode,
                            make_targets=make_targets,
                            project_flavor=project_flavor,
                            python_version_mode=python_version_mode,
                        )
                        list_of_specific_test_params.append(combo)
        generated_params = GeneratorForPytestParameterization.from_specific_test_params(
            list_of_specific_test_params)

        _LOGGER.debug("Finished generating basic combos of test parameters")
        return generated_params

