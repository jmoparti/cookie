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
        'dependency_management_mode',
        'make_targets',
        'project_flavor',
        'python_version_mode',
    ])


