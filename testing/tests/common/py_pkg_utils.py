# -*- coding: utf-8 -*-
"""
Utilities for introspecting on Python packages.

Patched in from the sysops-pyrepo-lib
(https://git.edgecastcdn.net/sysops-incubator/sysops-pyrepo-lib/blob/develop/so_pyrepo_lib/py_pkgs.py)

"""

#
# Imports
#

# import core
import collections
import json
import logging
import pprint
import os
import zipfile

# import third party
import devpi_common.metadata as dc_metadata
import devpi_common.validation as dc_validation

import wheel.install
import wheel.pkginfo
import wheel.util

# this project


#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)

#
# Classes for Python package inspection
#

PackageFileMetaData = collections.namedtuple(
    'PackageFileMetaData',
    [
        'file_type',
        'path',
        'project_name',
        'py_version',
        'suffix',
        'version',
    ])
"""
A set of meta-data about a Python distribution package file.

Collected using devpi-common package

Arguments:
    py_version (str): Denotes which version of the Python runtime is this
        package file is compatible with.
    file_type (str): What type of Python package file is it?
    project_name (str): The name of the package represented by the file.
    version (str): The version of the package represented by the file.
    suffix (str): Suffix part of the file name, includes everything up to
        the 'project name' portion of the file name.
    path (str): The absolute path to the package file.

"""


ParsedWheelAttributes = collections.namedtuple(
    'ParsedWheelFileData',
    [
        'arity',
        'datadir_name',
        'distinfo_name',
        'compatibility_tags',
        'install_paths',
        'parsed_filename',
        'parsed_wheel_info',
        'record_name',
        'tags',
        'wheelinfo_name',
    ])
"""
"Parsed wheel attributes" collected using the wheel packages's wheel.install.WheelFile
class.

Arguments:
    arity (object): wheel.install.WheelFile().arity
    datadir_name (object): wheel.install.WheelFile().datadir_name
    distinfo_name (object): wheel.install.WheelFile().distinfo_name
    compatibility_tags (object): wheel.install.WheelFile().compatibility_tags
    install_paths (object): wheel.install.WheelFile().install_paths
    parsed_filename (object): wheel.install.WheelFile().parsed_filename
    parsed_wheel_info (object): wheel.install.WheelFile().parsed_wheel_info
    record_name (object): wheel.install.WheelFile().record_name
    tags (object): wheel.install.WheelFile().tags
    wheelinfo_name (object): wheel.install.WheelFile().wheelinfo_name
"""

ParsedWheelDistInfo = collections.namedtuple(
    'ParsedWheelDistInfo',
    ['description_rst', 'metadata', 'record', 'wheel', 'metadata_json', 'top_level_txt'])
"""
Parsed data files this sub-directory in the wheel zip file : {project-name}-{version}.dist-info

Arguments:
    description_rst (list): List of lines (as str) from the DESCRIPTION.rst file
    metadata (list): List of lines (as str) from the METADATA file
    record (list): List of lines (as str) from the RECORD file
    wheel (list): List of lines (as str) from the WHEEL file
    metadata_json (dict): Parsed JSON data from the metadata.json file
    top_level_txt (list): List of lines (as str) from the top_level.txt file
"""


class PackageInspector(object):
    """Utils for package inspection"""

    @staticmethod
    def get_meta_data(package_path):
        """Get package meta-data from a package distribution file.

        Arguments:
            package_path (str): Path to the package file to be inspected.
        Returns:
             PackageFileMetaData: The discovered meta-data
        """
        _LOGGER.debug(
            "Begin getting meta-data about a package from its file at %s",
            package_path)

        # verify the file exists etc.
        if not os.path.exists(package_path):
            raise Exception("Package path '{}' does not exist".format(package_path))
        base_name = os.path.basename(package_path)

        # scrape it for py version metadata
        try:
            (py_version, file_type) = dc_metadata.get_pyversion_filetype(
                base_name)
        except Exception:
            error_message = (
                "Error getting 'py_version' and 'file_type' metadata from "
                "possible package file {}").format(package_path)
            _LOGGER.exception(error_message)
            raise Exception(error_message)

        # scrape it for additional metadata
        try:
            (project_name, version, suffix) = dc_metadata.splitbasename(
                base_name)
        except Exception:
            error_message = (
                "Error getting 'project_name', 'version', 'suffix' from "
                "package file {}").format(package_path)
            _LOGGER.exception(error_message)
            raise Exception(error_message)

        meta_data = PackageFileMetaData(
            py_version=py_version,
            file_type=file_type,
            project_name=project_name,
            version=version,
            suffix=suffix,
            path=package_path)
        _LOGGER.debug("Got this metadata from package file %s : %s",
                      package_path, pprint.pformat(meta_data))
        _LOGGER.debug(
            "Finished getting meta-data about a package from its file at %s",
            package_path)
        return meta_data

    @staticmethod
    def validate_meta_data(meta_data):
        """
        Use devpi-common's metadata validation routines

        Arguments:
             meta_data (PackageFileMetaData): meta data to validate.
        Raises:
             Exception: If invalid
        """
        _LOGGER.debug("Begin validating meta data")
        isinstance(meta_data, PackageFileMetaData)
        raw_meta_data = {
            'name': meta_data.project_name,
            'version': meta_data.version,
        }
        try:
            dc_validation.validate_metadata(raw_meta_data)
        except Exception as error:
            _LOGGER.exception(
                "Meta data from failed validation by devpi-common %s", str(raw_meta_data))
            raise AssertionError("Invalid meta-data, see logs for details")
        else:
            _LOGGER.debug("Finished validating meta data")

    @staticmethod
    def is_wheel(package_path):
        """
        Check if the package is wheel format or not

        Arguments:
            package_path (str): Path to the package file to be inspected.
        Returns:
             bool: True if wheel, False if not
        """
        _LOGGER.debug("Begin checking if this is a wheel")

        dc_meta_data = PackageInspector.get_meta_data(package_path)
        _LOGGER.debug("Checking file_type value from devpi common metadata for file %s : %s",
                      package_path, pprint.pformat(dc_meta_data))
        is_wheel = dc_meta_data.file_type == 'bdist_wheel'

        _LOGGER.debug("Finished checking if this is a wheel")
        return is_wheel

    @staticmethod
    def parse_wheel_attributes(package_path):
        """
        Use `wheel.install.WheelFile` to parse the wheel "attributes"

        Arguments:
            package_path (str): Path to the package file to be inspected.
        Returns:
             ParsedWheelAttributes: tuple bucket with output from parsing the
                wheel attributes
        Raises:
            Exception: If package is not in wheel format, or just plain broken.
        """
        _LOGGER.debug("Begin parsing wheel attributes from %s", package_path)

        # first make sure its a wheel at all
        assert PackageInspector.is_wheel(package_path), \
            "devpi-common metadata for package {} has file type that is not wheel".format(
                package_path)

        # now extract stuff
        wheel_file = wheel.install.WheelFile(package_path)

        # convert compatibility tags
        normalized_compatibility_tags = next(wheel_file.compatibility_tags)

        # convert parsed_filename (its raw form is a _sre.SRE_Match object)
        normalized_parsed_filename = {
            'groups': wheel_file.parsed_filename.groups(),
            'pattern': wheel_file.parsed_filename.re.pattern,
        }

        # convert tags
        normalized_tags = next(wheel_file.tags)

        # special handling for email msg formatted attribute
        parsed_wheel_info_as_str = wheel_file.parsed_wheel_info.as_string()
        normalized_parsed_wheel_info = {}
        for line in str(parsed_wheel_info_as_str).splitlines():
            if line:
                key, value = line.split(':', 1)
                if key not in normalized_parsed_wheel_info:
                    normalized_parsed_wheel_info[key] = []
                normalized_parsed_wheel_info[key].append(value.strip())

        # final result
        result = ParsedWheelAttributes(
            arity=wheel_file.arity,
            compatibility_tags=normalized_compatibility_tags,
            datadir_name=wheel_file.datadir_name,
            distinfo_name=wheel_file.distinfo_name,
            install_paths=wheel_file.install_paths,
            parsed_filename=normalized_parsed_filename,
            parsed_wheel_info=normalized_parsed_wheel_info,
            record_name=wheel_file.record_name,
            tags=normalized_tags,
            wheelinfo_name=wheel_file.wheelinfo_name,
        )
        _LOGGER.debug("Parsed these wheel attributes from %s:\n%s",
                      package_path, pprint.pformat(result))

        # done
        _LOGGER.debug("Finished parsing wheel attributes from %s", package_path)
        return result

    @staticmethod
    def parse_wheel_dist_info(package_path):
        """
        Peeks in the wheel file (as a zip archive), and extracts contents the `*dist-info`
        sub-directory.

        Arguments:
            package_path (str): Path to the package file to be inspected.
        Returns:
             ParsedWheelDistInfo: tuple bucket with output from parsing the
                wheel dist-info directory
        Raises:
            Exception: If package is not in wheel format, or just plain broken.
        """
        _LOGGER.debug("Begin parsing wheel dist info files from %s", package_path)

        # first make sure its a wheel at all
        assert PackageInspector.is_wheel(package_path), \
            "devpi-common metadata for package {} has file type that is not wheel".format(
                package_path)

        # parse the wheel attributes to get the dist-info sub-directory name
        parsed_wheel_attributes = PackageInspector.parse_wheel_attributes(package_path)
        dist_info_dir = parsed_wheel_attributes.distinfo_name
        _LOGGER.debug("Looking for this dist info sub-dir in the package wheel: %s", dist_info_dir)

        # setup the mapping between data names and the original data file names
        data_to_filename_lookup = {
            'description_rst': '{}/DESCRIPTION.rst'.format(dist_info_dir),
            'metadata': '{}/METADATA'.format(dist_info_dir),
            'record': '{}/RECORD'.format(dist_info_dir),
            'wheel': '{}/WHEEL'.format(dist_info_dir),
            'metadata_json': '{}/metadata.json'.format(dist_info_dir),
            'top_level_txt': '{}/top_level.txt'.format(dist_info_dir),
        }

        # read the raw data
        _LOGGER.debug("Begin reading all the raw dist-info data")
        raw_data = {}
        with zipfile.ZipFile(package_path, 'r') as zip_file:
            _LOGGER.debug("Found these top-level files in the package %s: %s",
                          package_path,
                          pprint.pformat([item.filename for item in zip_file.filelist]))
            for data_name, zip_file_path in data_to_filename_lookup.items():
                data_file_zip_info = zip_file.getinfo(zip_file_path)
                _LOGGER.debug("Begin reading raw data from %s", zip_file_path)
                with zip_file.open(data_file_zip_info, 'r') as data_file:
                    raw_data[data_name] = data_file.read()
                _LOGGER.debug("Finished reading raw data from %s", zip_file_path)
        _LOGGER.debug("Finished reading all the raw dist-info data")

        # normalize the raw data
        _LOGGER.debug("Begin normalizing the raw dist-info data")
        normalized_data = {}
        for data_name, filename in data_to_filename_lookup.items():
            _LOGGER.debug("Begin normalizing %s data from original file %s", data_name, filename)
            # bail out if you didn't find raw data for this
            if data_name not in raw_data:
                raise Exception(
                    "Missing dataset {} in read raw data. Found datasets were {}".format(
                        data_name, str(raw_data.keys())))

            # do some rudimentary normalization on some of the pieces of data
            if data_name == 'metadata_json':
                normalized_data[data_name] = json.loads(raw_data[data_name])
            else:
                normalized_data[data_name] = raw_data[data_name].splitlines()
            _LOGGER.debug("Finished normalizing %s data from original file %s", data_name, filename)
        _LOGGER.debug("Finished normalizing the raw dist-info data")

        # mint a named tuple and return
        result = ParsedWheelDistInfo(**normalized_data)
        _LOGGER.debug("Parsed wheel dist info from %s is\n%s", package_path, pprint.pformat(result))

        _LOGGER.debug("Finished parsing wheel dist info files from %s", package_path)
        return result
