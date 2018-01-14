"""
Root module for tests
"""

#
# Imports
#

import logging
import os
import sys

#
# Kludges
#

def configure_python_logging():
    """Brute force config of python logging"""
    log_format = '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] [%(funcName)s] -- %(message)s'
    date_format = '%H:%M:%S'
    log_level = logging.DEBUG

    # attempt to get python log file path from shell env
    env_var_name = 'PYTEST_LOG_PATH'
    try:
        log_file_path = os.environ[env_var_name]
        assert log_file_path, "log file path from env var {} is empty string or None".format(env_var_name)
        logging.basicConfig(filename=os.path.abspath(log_file_path), filemode='w', level=log_level, format=log_format, datefmt=date_format)
    except Exception:
        # fallback to stderr
        logging.basicConfig(stream=sys.stderr, level=log_level, format=log_format, datefmt=date_format)
        logger = logging.getLogger(__name__)
        logger.exception("Unable to configure logging to file named in env variable '%s', so falling back to STDERR", env_var_name)

    # do some customization of loggers
    tests_logger = logging.getLogger('tests')
    tests_logger.setLevel(logging.DEBUG)

    post_gen_hook_logger = logging.getLogger('post_gen_project')
    post_gen_hook_logger.setLevel(logging.DEBUG)


configure_python_logging()
