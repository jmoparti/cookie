# -*- coding: utf-8 -*-
"""
Utilities for introspecting on Python dependencies/requirements.

"""

#
# Imports
#

# import core
import collections
import copy
import logging
import pprint
import os

# import third party
import pkg_resources
import pip.download
import pip.req.req_file

# this project

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)


#
# classes/functions
#

PythonDependencyMarker = collections.namedtuple(
    'PythonDependencyMarker',
    [
        'os_name',
        'sys_platform',
        'python_full_version',
        'python_version',
        'platform_version',
        'platform_machine',
        'python_implementation',
    ]
)
"""
A 'neutral' definition of a python dependency marker, reverse engineered from pip internals.
"""


PythonDependencySpecification = collections.namedtuple(
    'PythonDependencySpecification',
    [
        'name',
        'constraint',
        'extras',
        'markers',
        'specifiers',
    ])
"""
A 'neutral' definition of a Python dependency specification (pep-0508), reverse engineered from
pip internals.
"""


class PipRequirementsInspector(object):
    """
    Inspector for pip requirements

    WARNING:

    * Pip's authors (in their infinite wisdom) have refused to provide a solid API for
      programmatically working with their library.
    * So we are using their latest internal API for this testing.  And this may break in
      the future as they change their stuff.
    * But for now, it is a necessary evil due to the lack of other options
    """

    def __init__(self):
        pass

    def _mint_neutral_marker(self, pip_req_marker):
        """Mint a neutral marker from a raw pip req marker"""
        _LOGGER.debug("Minting neutral marker from raw pip req marker: %s", pprint.pformat(
            pip_req_marker))
        neutral_marker = PythonDependencyMarker(
            os_name=getattr(pip_req_marker, 'os_name', None),
            sys_platform=getattr(pip_req_marker, 'sys_platform', None),
            python_full_version=getattr(pip_req_marker, 'python_full_version', None),
            python_version=getattr(pip_req_marker, 'python_version', None),
            platform_version=getattr(pip_req_marker, 'platform_version', None),
            platform_machine=getattr(pip_req_marker, 'platform_machine', None),
            python_implementation=getattr(pip_req_marker, 'python_implementation', None),
        )
        return neutral_marker

    def _launder_pip_req_obj(self, pip_req_obj):
        _LOGGER.debug("Begin parsing raw pip.req object: %s", pprint.pformat(pip_req_obj))

        # launder the markers
        neutral_markers = []
        if pip_req_obj.markers is not None:
            _LOGGER.debug("Laundering markers: %s", pprint.pformat(pip_req_obj.markers))
            if isinstance(pip_req_obj.markers, collections.Iterable):
                for marker in pip_req_obj.markers:
                    neutral_markers.append(self._mint_neutral_marker(marker))
            else:
                neutral_markers.append(self._mint_neutral_marker(pip_req_obj.markers))

        # launder the specifiers
        neutral_specifiers = []
        if pip_req_obj.specifier._specs is not None:
            _LOGGER.debug("Laundering specifiers: %s", pprint.pformat(pip_req_obj.specifier))
            for item in pip_req_obj.specifier._specs:
                neutral_specifiers.append(str(item))

        # launder into neutral extras
        neutral_extras = [item for item in pip_req_obj.req.extras]

        # make the final deliverable
        neutral_req = PythonDependencySpecification(
            name=pip_req_obj.name,
            constraint=pip_req_obj.constraint,
            markers=neutral_markers,
            extras=neutral_extras,
            specifiers=neutral_specifiers,
        )
        _LOGGER.debug("Parsed raw pip.req object %s into %s",
                      pprint.pformat(pip_req_obj), pprint.pformat(neutral_req))
        return neutral_req

    def parse_requirements_from_file(self, path):
        """
        Parse a pip requirements text file.

        Arguments:
            path (str): Path to a pip requirements text file

        Returns:
            list: A list of PythonDependencySpecification objects
        """
        _LOGGER.debug("Begin parsing pip requirements file %s", path)
        pip_session = pip.download.PipSession()
        parsed_requirements = []
        for pip_req in pip.req.req_file.parse_requirements(path, session=pip_session):
            parsed_requirements.append(self._launder_pip_req_obj(pip_req))

        _LOGGER.debug("Parsed requirements from path %s are: %s",
                      path, pprint.pformat(parsed_requirements))

        _LOGGER.debug("Finished parsing pip requirements file %s", path)
        return parsed_requirements

    def parse_requirement_from_str(self, requirement_str):
        """
        Parse a pip requirement from a string

        Arguments:
            requirement_str (str): Path to a pip requirements text file

        Returns:
            PythonDependencySpecification: The equivalent PythonDependencySpecification object
        """
        _LOGGER.debug("Begin parsing pip requirement str '%s'", requirement_str)
        pip_req = pip.req.InstallRequirement.from_line(requirement_str)
        parsed_requirement = self._launder_pip_req_obj(pip_req)

        _LOGGER.debug("Parsed requirement from str '%s' into %s",
                      requirement_str, pprint.pformat(parsed_requirement))

        _LOGGER.debug("Finished parsing pip requirements str '%s'", requirement_str)
        return parsed_requirement
