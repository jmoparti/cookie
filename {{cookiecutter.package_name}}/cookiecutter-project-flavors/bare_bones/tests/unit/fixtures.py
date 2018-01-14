# -*- coding: utf-8 -*-
# vim: ft=python
"""
Pytest fixtures usable across all unit tests
"""

#
# Imports
#

# core
import logging

# third party
import pytest

# this project

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)

# imports to others
__all__ = []

#
# Fixtures
#


@pytest.fixture(scope="function")
def example_unit_test_fixture():
    """fixture for unit tests"""
    return {}
