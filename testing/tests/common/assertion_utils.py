# -*- coding: utf-8 -*-
"""
Utilities for test assertions
"""

#
# Imports
#

# import core
import copy
import logging
import pprint
import os

# import third party
import pytest
import ruamel.yaml as yaml
import testfixtures

# this project
from tests.constants import (
    DependencyManagementMode,
    ProjectFlavor,
    PythonVersion,
    PythonVersionMode,
    PipRequirementsFile,
    TravisLanguage,
    ECTravisLanguage,
)
from tests.fixtures import (
    BasicTestParams,
)
from tests.common.cookiecutter_utils import (
    CookiecutterExtraContextSchema,
    CookiecutterJSONField,
)
from tests.common.py_pkg_utils import (
    PackageInspector,
)
from tests.common.py_dep_utils import (
    PipRequirementsInspector,
)
from tests.common.cookiecutter_utils import (
    CookiecutterExtraContextBuilder,
)

# logger
_LOGGER = logging.getLogger(__name__)


#
# Helper classes
#

class FileSystemSpec(object):
    """Specification of included / excluded files under a directory"""

    @staticmethod
    def _get_paths_by_python_version(python_version):
        """Get relative paths specific to a python version"""
        assert isinstance(python_version, PythonVersion)
        # - FYI -
        # In earlier versions of the cookiecutter, there are used to be file names/paths that were
        # specifically named with `py{xyz}` in their name.
        # But for the foreseeable future, we don't need them anymore.
        # However, going to leave this stub in place just in case.  As it was a pain to get right
        # in the first place.
        relative_paths = []
        return relative_paths

    def __init__(self, root_origin_directory, root_target_directory, cookiecutter_extra_context):
        _LOGGER.debug("Building file system spec object with: %s", locals())
        self.origin_dir_root = os.path.abspath(root_origin_directory)
        self.tgt_dir_root = os.path.abspath(root_target_directory)
        CookiecutterExtraContextSchema.raise_if_invalid(cookiecutter_extra_context)
        self.cookiecutter_extra_context = cookiecutter_extra_context
        self.include = set()
        self.exclude = set()
        self.file_modes = {}

    def include_path(self, relative_path):
        """Add a path relative to the root target directory to the include list"""
        _LOGGER.debug("Add this relative_path in the includes list: %s", relative_path)
        assert relative_path
        assert relative_path not in self.exclude
        self.include.add(os.path.join(self.tgt_dir_root, relative_path))

    def exclude_path(self, relative_path):
        """Add a path relative to the root target directory to the include list"""
        _LOGGER.debug("Add this relative_path in the excludes list: %s", relative_path)
        assert relative_path
        assert relative_path not in self.include
        self.exclude.add(os.path.join(self.tgt_dir_root, relative_path))

    def specify_by_project_flavor(self, project_flavor):
        """Update the file system spec based on the ProjectFlavor"""
        _LOGGER.debug("Updating the file system spec based on project flavor: %s", project_flavor)
        assert isinstance(project_flavor, ProjectFlavor)

        # get root module name from extra context
        root_module_name = self.cookiecutter_extra_context[
            CookiecutterJSONField.ROOT_MODULE_NAME.json_name]
        _LOGGER.debug("root module name is %s", root_module_name)

        # set constant name for staging folder
        staging_folder_name = 'cookiecutter-project-flavors'

        # add staging folder to exclude list, should not appear in output
        self.exclude_path(os.path.join(root_module_name, staging_folder_name))

        # populate include list
        project_flavor_origin_path = os.path.join(
            self.origin_dir_root,
            '{{cookiecutter.package_name}}',
            staging_folder_name,
            project_flavor.json_value,
        )
        _LOGGER.debug("Origin path for project flavor %s is %s", project_flavor,
                      project_flavor_origin_path)
        relative_dir_path_replace_pattern = "{}/".format(project_flavor_origin_path)
        for dir_path, dir_names, file_names in os.walk(project_flavor_origin_path):
            abs_dir_path = os.path.abspath(dir_path)
            relative_dir_path = abs_dir_path.replace(relative_dir_path_replace_pattern, '')
            relative_dir_path = relative_dir_path.replace('{{cookiecutter.root_module_name}}',
                                                          root_module_name)
            _LOGGER.debug("relative destination dir path is %s", relative_dir_path)
            if abs_dir_path != project_flavor_origin_path:
                self.include_path(relative_dir_path)
            for file_name in file_names:
                if file_name not in ['.gitignore']:
                    self.include_path(os.path.join(relative_dir_path, file_name))
        return self

    def specify_by_python_version_mode(self, python_version_mode):
        """Update the file system spec based on the PythonVersionMode"""
        _LOGGER.debug("Updating the file system spec based on python version mode: %s",
                      python_version_mode)
        assert isinstance(python_version_mode, PythonVersionMode)

        # include stuff that matches the version mode
        included_python_versions = set(python_version_mode.python_versions)
        for python_version in included_python_versions:
            relative_paths = FileSystemSpec._get_paths_by_python_version(python_version)
            for relative_path in relative_paths:
                self.include_path(relative_path)

        # exclude everything else
        excluded_python_versions = set(PythonVersion) - included_python_versions
        for python_version in excluded_python_versions:
            relative_paths = FileSystemSpec._get_paths_by_python_version(python_version)
            for relative_path in relative_paths:
                self.exclude_path(relative_path)

        return self

    def specify_file_mode(self, relative_path, bit_masks):
        """Specify an expected file mode as a bit mask for the relative path"""
        _LOGGER.debug(
            "Specifying a file mode for relative path %s using bit masks: %s", relative_path,
            bit_masks)
        assert relative_path
        assert relative_path not in self.exclude
        assert relative_path not in self.file_modes
        assert bit_masks
        self.file_modes[relative_path] = set()
        for bit_mask in bit_masks:
            self.file_modes[relative_path].add(bit_mask)
        return self

    def assert_includes(self):
        """Run the test assertion for includes"""
        _LOGGER.info("Begin asserting the include file list")
        for path in self.include:
            assert os.path.exists(path), "Expected path {} to exist".format(path)
        _LOGGER.info("Finished asserting the include file list")
        return self

    def assert_excludes(self):
        """Run the test assertion for excludes"""
        _LOGGER.info("Begin asserting the exclude file list")
        for path in self.exclude:
            assert not os.path.exists(path), "Expected path {} to NOT exist".format(path)
        _LOGGER.info("Finished asserting the exclude file list")
        return self

    def assert_file_modes(self):
        """Assert file modes"""
        _LOGGER.info("Begin asserting specified file modes")
        for relative_path in sorted(self.file_modes.keys()):
            abs_path = os.path.join(self.tgt_dir_root, relative_path)
            stat_result = os.stat(abs_path)
            for bit_mask in self.file_modes[relative_path]:
                assert bool(stat_result.st_mode & bit_mask), \
                    "'AND' of os.stat() result {} and bit mask {} for path {} was not true".format(
                        stat_result, bit_mask, relative_path)
        _LOGGER.info("Finished asserting specified file modes")
        return self

    def assert_all(self):
        """Run all possible assertions"""
        _LOGGER.info("Begin running all possible assertions")
        self.assert_includes().assert_excludes().assert_file_modes()
        _LOGGER.info("Finished running all possible assertions")
        return self


class PipRequirementsFileSpec(object):
    """
    Specification to assert/test Pip requirements txt files.

    WARNING:
         * Pip's authors (in their infinite wisdom) have refused to provide a solid API for
           programmatically working with their library.
         * So we are using their latest internal API for this testing.  And this may break in
           the future as they change their stuff.
         * But for now, it is a necessary evil due to the lack of other options
    """

    def __init__(self, project_output_path):
        self._project_output_path = project_output_path
        self._inspector = PipRequirementsInspector()

    def parse_requirements(self, pip_requirements_file_enum):
        """
        Asserts that all the known requirements files are parseable

        Arguments:
            pip_requirements_file_enum(PipRequirementsFile): Which pip requirements file from the
                emitted project you want to parse
        Returns:
            list: A list of pkg_resources.Requirements objects
        """
        _LOGGER.debug("Begin parsing requirements from %s", pip_requirements_file_enum)

        assert isinstance(pip_requirements_file_enum, PipRequirementsFile)
        path = os.path.join(self._project_output_path, pip_requirements_file_enum.file_name)
        parsed_requirements = self._inspector.parse_requirements_from_file(path)
        _LOGGER.debug("Finished parsing requirements from %s", pip_requirements_file_enum)
        return parsed_requirements

    def assert_requirements_files(self):
        """
        Do basic assertions on pip requirements files
        """
        _LOGGER.debug("Begin assertions on pip requirements files")

        for pip_req_file_enum in PipRequirementsFile:
            parsed_reqs = self.parse_requirements(pip_req_file_enum)
            assert parsed_reqs

        _LOGGER.debug("Finished assertions on pip requirements files")


class PythonPackageSpec(object):
    """Specification to assert/test Python packages"""

    def __init__(self, cookiecutter_json_data, specific_test_params, project_output_path):
        """
        Constructor

        Arguments:
            cookiecutter_json_data (dict): Baseline cookiecutter JSON data
            specific_test_params (tuple): A specific set of test parameters represented as a tuple.
            project_output_path (str): Path to the root directory of the project output
        """
        # save off the path
        self._project_output_path = project_output_path

        # create the base context based off the json obj
        builder = CookiecutterExtraContextBuilder()
        self._cookiecutter_extra_context = builder.build_from_json_and_test_params(
            cookiecutter_json_data, specific_test_params)

        # extract some expected values
        self._expected_values = {
            'package_name': self._cookiecutter_extra_context[
                CookiecutterJSONField.PACKAGE_NAME.json_name],
            'package_version': self._cookiecutter_extra_context[
                CookiecutterJSONField.PACKAGE_VERSION.json_name],
            'root_module_name': self._cookiecutter_extra_context[
                CookiecutterJSONField.ROOT_MODULE_NAME.json_name]
        }
        self._expected_values['project_name'] = \
            self._expected_values['package_name'].replace('-', '_')

        # setup delegates
        self._pkg_inspector = PackageInspector()

    def assert_basic_meta_data(self, package_path):
        """
        Assert the metadata of the the Python package file matches expectations.

        Arguments:
            package_path (str): Path to the Python package file
        """
        _LOGGER.debug("Begin asserting metadata for %s", package_path)

        raw_found_metadata = self._pkg_inspector.get_meta_data(package_path)
        _LOGGER.debug("Found raw metadata: %s", str(raw_found_metadata))

        try:
            self._pkg_inspector.validate_meta_data(raw_found_metadata)
        except AssertionError as error:
            pytest.fail("Package at {} failed metadata validation: {}".format(package_path, error))
        else:
            expected_metadata = {
                key: self._expected_values[key] for key in ['project_name', 'package_version']
            }
            found_metadata = {
                'project_name': raw_found_metadata.project_name,
                'package_version': raw_found_metadata.version,
            }
            testfixtures.compare(expected_metadata, found_metadata)

        _LOGGER.debug("Finished asserting metadata for %s", package_path)

    def _assert_install_requirements(self, parsed_wheel_dist_info):
        _LOGGER.debug("Compare pip requirements files with the metadata.json in the wheel")
        pip_req_inspector = PipRequirementsInspector()

        # get the install reqs as described in the requirements.txt file
        pip_req_from_req_txt = pip_req_inspector.parse_requirements_from_file(
            os.path.join(self._project_output_path, PipRequirementsFile.REQUIREMENTS_TXT.file_name))
        _LOGGER.debug("Got these pip reqs from the requirements.txt file:\n%s",
                      pprint.pformat(pip_req_from_req_txt))
        pkg_names_from_req_txt = set()
        for item in pip_req_from_req_txt:
            pkg_names_from_req_txt.add(item.name)

        # get the install reqs from the metadata.json from the wheel dist info
        pip_req_from_dist_info = []
        for run_requires_entry in parsed_wheel_dist_info.metadata_json.get('run_requires', []):
            _LOGGER.debug("run requires entry is %s", pprint.pformat(run_requires_entry))
            if 'requires' in run_requires_entry:
                for item in run_requires_entry['requires']:
                    pip_req_from_item = pip_req_inspector.parse_requirement_from_str(str(item))
                    pip_req_from_dist_info.append(pip_req_from_item)

        _LOGGER.debug("Got these pip reqs from the metadata.json dist-info file:\n%s",
                      pprint.pformat(pip_req_from_dist_info))
        pkg_names_from_dist_info = set()
        for item in pip_req_from_dist_info:
            pkg_names_from_dist_info.add(item.name)

        # compare the name sets
        _LOGGER.debug(
            "Comparing dependency package names between pip requirements.txt and dist-info "
            "metadata.json (%s vs %s)", str(pkg_names_from_req_txt), str(pkg_names_from_dist_info))
        testfixtures.compare(pkg_names_from_req_txt, pkg_names_from_dist_info)

    def assert_package_contents(self, package_path):
        """
        Assert the package contents are "good"
        """
        _LOGGER.debug("Begin assert package")

        # parse the wheel dist-info
        _LOGGER.debug("Get the parsed dist info from the wheel")
        parsed_wheel_dist_info = self._pkg_inspector.parse_wheel_dist_info(package_path)

        # assert simple stuff
        _LOGGER.debug("Assert the basics")
        expected = copy.deepcopy(self._expected_values)
        del expected['project_name']
        found = {
           'root_module_name': parsed_wheel_dist_info.top_level_txt[0].strip(),
           'package_name': parsed_wheel_dist_info.metadata_json['name'],
           'package_version': parsed_wheel_dist_info.metadata_json['version'],
        }
        testfixtures.compare(expected, found)

        _LOGGER.debug("Sanity check the install requirements expressed in the metadata.json")
        self._assert_install_requirements(parsed_wheel_dist_info)

        _LOGGER.debug("Finished assert package")


class TravisFileSpec(object):
    """
    Specification to assert/test travis-related files.

    """

    def __init__(self, project_output_path):
        self._project_output_path = project_output_path

    def assert_dot_travis_yml(self, dependency_managemeent_mode, python_version_mode):
        """
        Asserts some basic stuff about the .travis.yml file.

        WARNING:
            * Only checks for valid YAML, does NOT do any travis specific logic.
        """
        fn_args = locals()
        _LOGGER.debug("Begin assertions about .travis.yml using args %s", str(fn_args))
        assert isinstance(dependency_managemeent_mode, DependencyManagementMode)
        assert isinstance(python_version_mode, PythonVersionMode)

        # formulate the path
        path = os.path.join(self._project_output_path, '.travis.yml')
        _LOGGER.debug("Doing assertions on .travis.yml file at %s", path)
        assert os.path.exists(path), "Path to .travis.yml does not exist: '{}'".format(path)

        # do basic yaml parse
        yaml_parser = yaml.YAML(typ='safe')
        with open(path, 'r') as yaml_file:
            yaml_data = yaml_parser.load(yaml_file)
            _LOGGER.debug("Was able to read .travis.yml YAML file successfully")

        # assert common stuff
        for field_name in ['language', 'install', 'script']:
            assert field_name in yaml_data, "'{}' field was missing from .travis.yml at {}".format(
                field_name, path)

        # assert things specific to combinations of project settings
        if dependency_managemeent_mode == DependencyManagementMode.MANAGED_IN_HOUSE:
            # assert language
            assert yaml_data['language'] == ECTravisLanguage.DEB_1404.field_value, \
                ".travis.yml 'language' field is not set to {} : '{}'".format(
                    ECTravisLanguage.DEB_1404.field_value, yaml_data['language'])

            # assert the lack of matrix
            assert 'matrix' not in yaml_data, "'matrix' field is present in the .travis.yml and shouldn't be"

            # assert the env
            assert 'env' in yaml_data, "'env' field is missing from .travis.yml"
            env_value = yaml_data['env']
            assert isinstance(env_value, list), "'env' field doesn't have a list value '{}'".format(env_value)
            if python_version_mode == PythonVersionMode.PY27_ONLY:
                expected_env_value = ["TOXENV=py27 DEFAULT_PY_ENV=py27"]
            elif python_version_mode == PythonVersionMode.PY27_THRU_PY3:
                expected_env_value = ['''TOXENV="py27,py34" DEFAULT_PY_ENV=py34''']
            elif python_version_mode == PythonVersionMode.PY3_ONLY:
                expected_env_value = ["TOXENV=py34 DEFAULT_PY_ENV=py34"]
            else:
                raise Exception("Unsupported PythonVersionMode {}".format(python_version_mode))
            testfixtures.compare(expected_env_value, env_value)

            # assert the deploy
            assert 'deploy' in yaml_data, "'deploy' field is missing from .travis.yml"
        elif dependency_managemeent_mode == DependencyManagementMode.PUBLIC_THIRD_PARTIES:
            # assert language
            assert yaml_data['language'] == TravisLanguage.PYTHON.field_value, \
                ".travis.yml 'language' field is not set to {} : '{}'".format(
                    TravisLanguage.PYTHON.field_value, yaml_data['language'])

            # assert the matrix
            assert 'matrix' in yaml_data, "'matrix' field is missing from .travis.yml"
            matrix_value = yaml_data['matrix']
            assert 'include' in matrix_value, "'include' field is missing from the matrix field of the .travis.yml"
            matrix_include_value = matrix_value['include']
            expected_matrix_include_value = []
            if python_version_mode in [PythonVersionMode.PY27_ONLY, PythonVersionMode.PY27_THRU_PY3]:
                expected_matrix_include_value.append(
                    {
                        'python': "2.7",
                        'env': "TOXENV=py27",
                    }
                )
            if python_version_mode in [PythonVersionMode.PY27_THRU_PY3, PythonVersionMode.PY3_ONLY]:
                expected_matrix_include_value.append(
                    {
                        'python': "3.4",
                        'env': "TOXENV=py34",
                    }
                )
            testfixtures.compare(expected_matrix_include_value, matrix_include_value)

            # assert the lack of env
            assert 'env' not in yaml_data, "'env' field is present in the .travis.yml and shouldn't be"

            # assert the lack of deploy
            assert 'deploy' not in yaml_data, "'deploy' field is present in the .travis.yml when it shouldn't be"

        else:
            raise Exception("Unsupported dependency management mode {}".format(dependency_managemeent_mode))

        _LOGGER.debug("Finished assertions about .travis.yml using args %s", str(fn_args))
