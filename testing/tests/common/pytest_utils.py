# -*- coding: utf-8 -*-
"""
Utilities related to pytest plumbing
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

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)


#
# Functions
#

def skip_if_missing_python_interpreter(python_version_enum):
    """Skip test if missing the necessary version of the Python interpreter"""
    file_name = python_version_enum.executable_name
    if not shutilwhich.which(file_name):
        message = "Missing the necessary version of the Python interpreter: {}".format(file_name)
        pytest.skip(message)

