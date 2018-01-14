# -*- coding: utf-8 -*-
"""
Utilities for messing with Git for test purposes
"""

#
# Imports
#

# import core
import logging

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

def prepare_minimal_viable_git_repo(repo_path):
    """Prepare a minimal viable git repo in the path"""
    run_params = locals()
    _LOGGER.debug("Begin preparing a minimally viable git repo: %s", run_params)

    try:
        cmd_texts = [
            'git init',
            'git add .gitignore',
            'git add .',
            'git status',
        ]
        for cmd_text in cmd_texts:
            run_shell(cmd_text, working_path=repo_path)
    except Exception as error:
        msg = "Invocation of git during test failed"
        _LOGGER.exception(msg)
        raise Exception("{}.  See logs for details".format(msg))
    else:
        _LOGGER.debug("Finished preparing a minimally viable git repo: %s", run_params)


