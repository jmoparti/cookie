# -*- coding: utf-8 -*-
"""
Utilities for invoking Vagrant
"""

#
# Imports
#

# import core
import logging
import os

# import third party

# this project
from tests.common.misc_utils import (
    run_shell,
)

# logger
_LOGGER = logging.getLogger(__name__)


#
# Helper stuff
#


def invoke_vagrant_command(working_path, vagrant_commands):
    """Run vagrant under test"""
    run_params = locals()
    _LOGGER.debug("Begin invoking the vagrant under test with: %s", run_params)

    # assert that there is a Vagrantfile in the working dir
    assert os.path.exists(os.path.join(working_path, 'Vagrantfile')), \
        "No Vagrantfile was found in working path {}".format(working_path)

    try:
        for vagrant_command in vagrant_commands:
            cmd_text = "vagrant {}".format(vagrant_command)
            _LOGGER.debug("Invoking this vagrant command: '%s'", cmd_text)
            run_shell(cmd_text, working_path=working_path)
    except Exception as error:
        _LOGGER.exception("Invocation of vagrant under test failed!")
        raise Exception("Cookiecutter failed, see log file")
    else:
        _LOGGER.debug("Finished invoking the vagrant under test with: %s", run_params)
