# -*- coding: utf-8 -*-
"""
Make-related utilities
"""

#
# Imports
#

# import core
import copy
import logging
import os
import re
import sys

# import third party
import pytest

# this project
from tests.constants import (
    MakeTarget,
)
import tests.common.misc_utils
import tests.common.output_utils
from tests.make.common.misc_utils import (
    SpecificTestParams,
)

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)


#
# Classes / functions
#

def compose_make_command(make_targets):
    """compose make command text from zero or more make targets"""
    if make_targets:
        cmd_text = "make {}".format(" ".join(MakeTarget.format_for_make(make_targets)))
    else:
        cmd_text = "make"
    return cmd_text


def run_make_on_host(specific_test_params, project_output_path):
    """Run make in the project that was emitted on the host"""
    assert isinstance(specific_test_params, SpecificTestParams)
    make_cmd_text = compose_make_command(specific_test_params.make_targets)
    try:
        tests.common.misc_utils.run_shell(make_cmd_text, project_output_path)
    except Exception as error:
        _LOGGER.exception("Command '%s' failed (see previous STDERR): %s", make_cmd_text, error)
        pytest.fail("Command, {}, failed, see log file for details: {}".format(
            make_cmd_text, error))
    else:
        _LOGGER.debug("Successfully ran make in a shell: '%s'", make_cmd_text)


def parse_makefile(project_output_path):
    """
    Rudimentary parsing of makefile.

    Only scrapes makefile target names right now.
    """
    _LOGGER.debug("Begin rudimentary parsing of makefile")
    path = os.path.join(project_output_path, 'Makefile')

    makefile_target_regex = re.compile(r'^(\w+):')
    parsed_makefile = {'targets': []}

    with open(path, 'r') as input_file:
        for line in input_file.readlines():
            _LOGGER.debug("Parsing line '%s'", str(line))
            match_obj = re.match(makefile_target_regex, line)
            if match_obj:
                target_name = match_obj.group(1)
                parsed_makefile['targets'].append(target_name)
    _LOGGER.debug("Parsed makefile is %s", str(parsed_makefile))

    _LOGGER.debug("Finished rudimentary parsing of makefile")
    return parsed_makefile


class MakeTargetPermutationBuilder(object):
    """Utility for building permutations of make file targets"""

    DEFAULT_MAKE_TARGET = MakeTarget.ALL

    def __init__(self):
        self._tree = MakeTarget.build_target_tree()

    def get_the_default_target(self):
        """Get the default makefile target"""
        return MakeTargetPermutationBuilder.DEFAULT_MAKE_TARGET

    def get_targets_called_by(self, make_target):
        """Get the make targets called by this make target"""
        assert isinstance(make_target, MakeTarget)
        targets = copy.deepcopy(self._tree[make_target])
        return targets

    def get_targets_called_by_default(self):
        """Get list of make targets called by default"""
        default_targets = self._tree[MakeTargetPermutationBuilder.DEFAULT_MAKE_TARGET]
        return copy.deepcopy(default_targets)

    def get_targets_not_called_by_default(self):
        """
        Get make targets which won't be called by default.

        Whenever possible get an apex target rather than enumerate its children
        """
        targets = []
        targets_called_by_default = self.get_targets_called_by_default()

        # first pass to get make targets which are not called by default and which call other
        # targets
        for make_target in self._tree.keys():
            if make_target not in targets_called_by_default and self._tree[make_target]:
                targets.append(make_target)

        # second pass
        for make_target in self._tree.keys():
            if make_target not in targets_called_by_default and make_target not in targets:
                targets.append(make_target)

        return targets





