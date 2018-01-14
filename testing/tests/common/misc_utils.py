# -*- coding: utf-8 -*-
"""
Miscellaneous utility functions for tests.
"""

#
# Imports
#

# import core
import collections
import contextlib
import logging
import StringIO
import subprocess
import sys

# import third party
import pytest
import shutilwhich

# this project

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)

#
# Configure python logging
#

_LOGGING_FORMAT = \
    '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] [%(funcName)s] -- %(message)s'
_LOGGING_DATE_FORMAT = '%H:%M:%S'


def configure_python_logging(log_file_path):
    """Brute force hack to get logging working"""

    logging.basicConfig(filename=log_file_path,
                        mode='w',
                        level=logging.DEBUG,
                        format=_LOGGING_FORMAT,
                        datefmt=_LOGGING_DATE_FORMAT)

    tests_logger = logging.getLogger('tests')
    tests_logger.setLevel(logging.DEBUG)

    post_gen_hook_logger = logging.getLogger('post_gen_project')
    post_gen_hook_logger.setLevel(logging.DEBUG)


#
# Named tuples
#

BasicTestParams = collections.namedtuple(
    'BasicTestParams',
    [
        'repo_root_path',
        'cookiecutter_config_path',
        'cookiecutter_json_data',
        'root_output_path',
        'retain_passed_test_data',
    ])

SpecificTestParamsFilter = collections.namedtuple(
    'SpecificTestParamsFilter',
    [
        'dependency_management_mode',
        'project_flavor',
        'python_version_mode',
        'make_targets',
    ])


#
# Context manager for redirecting std{out|err}
#

@contextlib.contextmanager
def redirected_stdout_and_stderr():
    """Context manager for temporarily redirecting stdout/error to the python logging"""

    real_stdout = None
    real_stderr = None
    stdout_buffer = StringIO.StringIO()
    stderr_buffer = StringIO.StringIO()
    try:
        real_stdout = sys.stdout
        real_stderr = sys.stderr
        sys.stdout = stdout_buffer
        sys.stderr = stderr_buffer
        yield
    finally:
        if real_stdout is not None:
            sys.stdout = real_stdout
            _LOGGER.debug("Buffered STDOUT was\n%s", stdout_buffer)
        if real_stderr is not None:
            sys.stderr = real_stderr
            _LOGGER.debug("Buffered STDERR was\n%s", stderr_buffer)


#
# Functions
#

def skip_if_missing_python_interpreter(python_version_enum):
    """Skip test if missing the necessary version of the Python interpreter"""
    file_name = python_version_enum.executable_name
    if not shutilwhich.which(file_name):
        message = "Missing the necessary version of the Python interpreter: {}".format(file_name)
        pytest.skip(message)


def run_shell(cmd_text, working_path):
    """
    Shell command runner which streams its output to the common test log.
    """
    _LOGGER.debug("Begin running subprocess shell in directory %s with command: '%s'",
                  working_path, cmd_text)

    sub_proc = subprocess.Popen(
        cmd_text,
        shell=True,
        cwd=working_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    for line in iter(sub_proc.stdout.readline, b''):
        _LOGGER.debug(line.strip())
    sub_proc.wait()
    assert sub_proc.returncode == 0, \
        "Non-zero exit code, {}, from running shell command in directory {}: '{}'".format(
            sub_proc.returncode, working_path, cmd_text)

    _LOGGER.debug("Finished running subprocess shell in directory %s with command: '%s'",
                  working_path, cmd_text)

