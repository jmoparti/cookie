# -*- coding: utf-8 -*-
#
# Imports
#

# import core
import logging

# import third party
import pytest

# import your test scaffolding

# marks everything in here
pytestmark = pytest.mark.integration_test

# logger
_LOGGER = logging.getLogger(__name__)

#
# Tests
#

def test_no_op(example_int_test_fixture):
    assert True
