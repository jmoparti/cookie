# -*- coding: utf-8 -*-
"""
Utilities for managing the working/output directories for tests
"""

#
# Imports
#

# import core
import hashlib
import logging
import pprint
import os
import shutil

# import third party

# this project
import tests.constants
import tests.fixtures
import tests.common.misc_utils
import tests.common.cookiecutter_utils

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)


#
# Functions
#

def _safer_rmtree(path):
    """Semi-safe rmtree"""
    abs_path = os.path.abspath(path)
    assert os.path.isdir(path)
    assert not abs_path.strip() == '/'
    assert not abs_path.startswith('..')
    assert not abs_path.startswith('.')
    _LOGGER.debug("Removing directory tree at %s", abs_path)
    shutil.rmtree(abs_path, ignore_errors=False)

#
# Classes for output directory setup etc.
#


class OutputDirectoryManager(object):
    """Manager for output directories used by tests"""

    @staticmethod
    def build_params_hash(specific_test_params):
        """Make a semi-unique hash out of a prefix plus params"""
        # verify params
        assert isinstance(specific_test_params, tuple)

        # calc hash
        hash_obj = hashlib.sha1()
        hash_obj.update("{}{}".format(specific_test_params.__class__, specific_test_params))
        full_hash_hex = hash_obj.hexdigest()
        short_hash_hex = full_hash_hex[-4:]
        return short_hash_hex

    @staticmethod
    def _get_output_dir_path(basic_test_params, prefix, hash_value):
        assert isinstance(basic_test_params, tests.fixtures.BasicTestParams)
        assert prefix
        assert hash_value
        sub_directory_name = "{}-{}".format(prefix, hash_value)
        output_dir_path = os.path.join(basic_test_params.root_output_path, sub_directory_name)
        return output_dir_path

    def __init__(self, basic_test_params, specific_test_params, prefix):
        assert isinstance(basic_test_params, tests.fixtures.BasicTestParams)
        assert isinstance(specific_test_params, tuple)
        self.basic_test_params = basic_test_params
        self.specific_test_params = specific_test_params
        self.output_prefix = prefix
        self.params_hash_value = OutputDirectoryManager.build_params_hash(self.specific_test_params)
        self.output_dir_path = OutputDirectoryManager._get_output_dir_path(
            self.basic_test_params, self.output_prefix, self.params_hash_value)

    def get_project_output_path(self):
        """
        Given the test output path and basic test params return the expected location of
        the emitted project template's root directory.
        """
        package_name = self.basic_test_params.cookiecutter_json_data[
            tests.common.cookiecutter_utils.CookiecutterJSONField.PACKAGE_NAME.json_name]
        project_output_path = os.path.join(self.output_dir_path, package_name)
        return project_output_path

    def setup(self):
        """Do the actual setup of the output directory in prep for testing with it"""
        _LOGGER.info("Begin setting up output directory: %s", self.output_dir_path)

        # remove any existing output directory
        if os.path.exists(self.output_dir_path):
            _LOGGER.debug("Found previous template output, removing it: %s", self.output_dir_path)
            _safer_rmtree(self.output_dir_path)
        os.mkdir(self.output_dir_path)
        _LOGGER.debug("Created output directory path: %s", self.output_dir_path)

        # make breadcrumb file with original parameters
        breadcrumb_data = {
            'params_hash_value': self.params_hash_value,
            'output_prefix': self.output_prefix,
            'basic_test_params': self.basic_test_params,
            'specific_test_params': self.specific_test_params,
        }
        breadcrumb_path = os.path.join(self.output_dir_path, "test-params.txt")
        with open(breadcrumb_path, 'w') as output_file:
            for key in sorted(breadcrumb_data.keys()):
                output_file.write("**** {} ****\n".format(key))
                pprint.pprint(breadcrumb_data[key], output_file)
                output_file.write("\n")
        _LOGGER.debug("Finished writing test params to breadcrumb file: %s", breadcrumb_path)

        # return path
        _LOGGER.info("Finished setting up output directory: %s", self.output_dir_path)
        return self.output_dir_path

    def tear_down(self):
        """Remove the test output directory"""
        _LOGGER.info("Begin tearing down (removing) output directory: %s", self.output_dir_path)
        _safer_rmtree(self.output_dir_path)
        _LOGGER.info("Finished tearing down (removing) output directory: %s", self.output_dir_path)
