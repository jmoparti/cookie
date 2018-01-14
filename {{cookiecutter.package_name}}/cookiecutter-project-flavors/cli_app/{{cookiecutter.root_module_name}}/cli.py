# -*- coding: utf-8 -*-
"""
{{cookiecutter.root_module_name}}.cli
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Command line entry point.
"""

#
# Imports
#

import argparse
import logging
import sys

#
# Module variables
#

_LOGGER = logging.getLogger(__name__)


#
# Functions
#

def _parse_cli_args():
    """Parse the command line arguments"""

    # get an instance of a parser
    parser = argparse.ArgumentParser()

    # setup logging flags
    logging_flags_group = parser.add_mutually_exclusive_group()
    logging_flags_group.add_argument(
        '--verbose', action='store_true', help="Show logging from INFO or above")
    logging_flags_group.add_argument(
        '--debug', action='store_true', help="Show logging from DEBUG or above")

    # here you'd setup any other arguments/flags you cared about

    # return result of parsing cli args
    return parser.parse_args()


def _configure_logging(log_level=None):
    """Configure logging"""
    logging_format = '%(asctime)s %(levelname)s %(module)s %(lineno)d %(name)s - %(message)s'
    if log_level is None:
        log_level = logging.WARNING
    logging.basicConfig(stream=sys.stderr, level=log_level, format=logging_format)


def _update_logging_config(parsed_args):
    """Update the logging config based on the parsed cli args"""
    if parsed_args.verbose:
        _configure_logging(log_level=logging.INFO)
    elif parsed_args.debug:
        _configure_logging(log_level=logging.DEBUG)


def main():
    """Command line entry point"""
    _configure_logging()
    parsed_args = _parse_cli_args()
    _update_logging_config(parsed_args)

    _LOGGER.info("Begin running")
    _LOGGER.debug("Here is where you'd put calls to functions etc that did the work of your app")
    _LOGGER.info("Finished running")
