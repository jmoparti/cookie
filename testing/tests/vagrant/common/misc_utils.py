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

# this project
import tests.fixtures

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
        'vagrant_vm',
        'python_version_mode',
        'python_repo_mode',
        'vagrant_box_mode',
    ])


#
# Functions
#


