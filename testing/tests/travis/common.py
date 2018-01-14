# -*- coding: utf-8 -*-
"""
Common scaffolding/utils for travis testing
"""

#
# Imports
#

# import core
import collections
import logging

# import third party

# this project
from tests.common.output_utils import (
    OutputDirectoryManager
)
from tests.common.cookiecutter_utils import (
    CookiecutterExtraContextBuilder,
)


#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)

#
# Classes
#

SpecificTestParams = collections.namedtuple(
    'SpecificTestParams',
    [
        'python_version_mode',
        'dependency_management_mode',
    ])


#
# Functions
#

def convert_specific_params_to_metafunc_arg_id(specific_test_params):
    """
    convert the values of the specific test params tuple into printable arg id
    for pytest test parameterization
    """
    assert isinstance(specific_test_params, SpecificTestParams)
    params_hash = OutputDirectoryManager.build_params_hash(specific_test_params)
    arg_id = '-'.join([
        specific_test_params.python_version_mode.name.lower(),
        specific_test_params.dependency_management_mode.name.lower(),
        params_hash,
    ])
    return arg_id


def mint_extra_context(cookiecutter_json_data, specific_test_params):
    """Mint a cookiecutter "extra context". """
    _LOGGER.debug("Begin minting a cookiecutter extra context")

    # verify parameters
    assert isinstance(specific_test_params, SpecificTestParams)

    # create the base context based off the json obj
    builder = CookiecutterExtraContextBuilder()
    extra_context = builder.build_from_json_and_test_params(
        cookiecutter_json_data, specific_test_params)

    _LOGGER.debug("Minted extra context: %s", extra_context)
    return extra_context
