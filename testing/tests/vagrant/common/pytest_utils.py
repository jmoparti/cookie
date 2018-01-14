# -*- coding: utf-8 -*-
"""
Utilities related to pytest plumbing specific to tests specific to makefile targets
"""

#
# Imports
#

# import core
import logging

# import third party
import pytest
import shutilwhich

# this project
from tests.common.output_utils import (
    OutputDirectoryManager
)
from tests.vagrant.common.misc_utils import (
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

def convert_specific_params_to_metafunc_arg_id(specific_test_params):
    """
    convert the values of the specific test params tuple into printable arg id
    for pytest test parameterization
    """
    assert isinstance(specific_test_params, SpecificTestParams)
    params_hash = OutputDirectoryManager.build_params_hash(specific_test_params)
    arg_id = '-'.join([
        specific_test_params.vagrant_vm.name.lower(),
        specific_test_params.vagrant_box_mode.name.lower(),
        specific_test_params.python_version_mode.name.lower(),
        specific_test_params.python_repo_mode.name.lower(),
        params_hash,
    ])
    return arg_id


def skip_if_no_vagrant_executable():
    """Skip the test if you cannot find the vagrant executable"""
    if not shutilwhich.which('vagrant'):
        pytest.skip("No vagrant executable found")
