# -*- coding: utf-8 -*-
# vim: ft=python
"""
Pytest plugin for establishing python logging config at test-time.
"""

#
# Imports
#

# core
import logging
import logging.config
import sys

# third party
import pytest

# this project

#
# module variables
#

_LOGGING_FORMAT = '[%(asctime)s] [%(levelname)s] [%(name)s] [%(filename)s:%(lineno)d] [%(funcName)s] -- %(message)s'
_DEFAULT_OUTPUT_PATH = 'pytest.log'

#
# hooks
#


def pytest_addoption(parser):
    """Add additional custom args"""
    parser.addoption('--pylog-output-path', help='Path for the python logging output file')


# pylint: disable=bare-except
@pytest.hookimpl(tryfirst=True)
def pytest_cmdline_main(config):
    """Configure python logging before kicking off command line"""
    try:
        output_path = config.getoption('pylog_output_path')
        if not output_path:
            output_path = _DEFAULT_OUTPUT_PATH

        #
        # We have to use dict config cause basicConfig() didn't quite work right in
        # terms of respecting existing loggers etc, and the way pytest loads
        # plugins during runtime
        #
        # Also we are using the file handler in append mode to allow for python-xdist
        # usage where you'd have multiple processes attempting to write to the same file.
        #

        config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': _LOGGING_FORMAT,
                },
            },
            'handlers': {
                'file_handler': {
                    'formatter': 'standard',
                    'class': 'logging.FileHandler',
                    'filename': output_path,
                    'mode': 'a',
                },
            },
            'loggers': {
                '': {
                    'handlers': ['file_handler'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
            },
        }

        logging.config.dictConfig(config)
        logger = logging.getLogger(__name__)
        logger.info("Successfully setup custom python logging configuration for this test run")
    except:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
        logger = logging.getLogger(__name__)
        logger.warning("Failed to setup custom python logging configuration", exc_info=True)
