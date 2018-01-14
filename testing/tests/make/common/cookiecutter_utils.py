# -*- coding: utf-8 -*-
"""
Miscellaneous utilities
"""

#
# Imports
#

# import core
import collections
import logging

# import third party
import pytest

# this project
from tests.common.cookiecutter_utils import (
    CookiecutterExtraContextBuilder,
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

