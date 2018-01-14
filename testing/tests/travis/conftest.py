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

# import to expose to pytest magic
from .fixtures import (
    github_token_for_travis_tests,
)

#
# Module stuff
#

# instantiate logger
_LOGGER = logging.getLogger(__name__)

#
# Hooks
#


