# -*- coding: utf-8 -*-

#
# Imports
#

# core python
import copy
import logging

# third party
import enum

#
# Module variables
#

# logging
_LOGGER = logging.getLogger(__name__)


#
# Enumerations
#

@enum.unique
class MakeTarget(enum.Enum):
    """Possible make targets to test"""

    ALL = 'all'
    BUILD = 'build'
    CLEAN = 'clean'
    CLEAN_ALL = 'clean_all'
    CLEAN_COVERAGE = 'clean_coverage'
    CLEAN_DIST = 'clean_dist'
    CLEAN_DOCS = 'clean_docs'
    CLEAN_LOGS = 'clean_logs'
    CLEAN_PYC = 'clean_pyc'
    CLEAN_TOX = 'clean_tox'
    CLEAN_TOX_OUTPUT = 'clean_tox_output'
    DEVELOP = 'develop'
    DOCS = 'docs'
    DOCS_DRAFT = 'docs_draft'
    FORMAT_WITH_YAPF = 'format_with_yapf'
    INTEGRATION_TESTS = 'integration_tests'
    LINT = 'lint'
    LINT_TESTS = 'lint_tests'
    TESTS = 'tests'
    TEST_WHEEL = 'test_wheel'
    SYSTEM_TESTS = 'system_tests'
    UNIT_TESTS = 'unit_tests'
    WHEEL = 'wheel'

    def __init__(self, target_name):
        self.target_name = target_name

    @staticmethod
    def format_for_make(make_targets):
        """Convert list of make target enums into make target text list"""
        if not make_targets:
            return make_targets
        make_targets_as_str = []
        for item in make_targets:
            assert isinstance(item, MakeTarget), "item '{}' is not an instance of {}".format(item, MakeTarget)
            make_targets_as_str.append(item.target_name)
        return make_targets_as_str

    @staticmethod
    def build_target_tree():
        """Return a tree representing the inter-dependencies amongst the make targets"""
        data = {
            MakeTarget.ALL: [
                MakeTarget.CLEAN,
                MakeTarget.BUILD,
                MakeTarget.LINT,
                MakeTarget.LINT_TESTS,
                MakeTarget.DOCS,
                MakeTarget.WHEEL],
            MakeTarget.CLEAN: [
                MakeTarget.CLEAN_COVERAGE,
                MakeTarget.CLEAN_DIST,
                MakeTarget.CLEAN_DOCS,
                MakeTarget.CLEAN_LOGS,
                MakeTarget.CLEAN_PYC,
                MakeTarget.CLEAN_TOX_OUTPUT
            ],
            MakeTarget.CLEAN_ALL: [MakeTarget.CLEAN, MakeTarget.CLEAN_TOX],
            MakeTarget.TEST_WHEEL: [MakeTarget.WHEEL],
        }
        for make_target in MakeTarget:
            if make_target not in data:
                data[make_target] = []
        return copy.deepcopy(data)

    @staticmethod
    def should_build_a_wheel(*make_targets):
        """Return true/false on whether the make target should result in a wheel"""
        _LOGGER.debug("Begin checking if this make target list %s should result in a wheel",
                      str(make_targets))
        try:
            tree = MakeTarget.build_target_tree()
            for make_target in make_targets:
                assert isinstance(make_target, MakeTarget)
                if make_target == MakeTarget.WHEEL:
                    _LOGGER.debug("the immediate make target, '%s', is the one to build a wheel")
                    return True
                if make_target in tree:
                    if MakeTarget.WHEEL in tree[make_target]:
                        _LOGGER.debug(
                            "the immediate make target, '%s', depends on one the one that "
                            "builds the wheel: '%s'", make_target, str(tree[make_target]))
                        return True
            return False
        finally:
            _LOGGER.debug("Finished checking if this make target list %s should result in a wheel",
                          str(make_targets))


@enum.unique
class ProjectFlavor(enum.Enum):
    """
    Enumeration of supported values for `cookiecutter.project_flavor`
    Ordered by default first.
    """

    BARE_BONES = 'bare_bones'
    LIBRARY = 'library'
    CLI_APP = 'cli_app'
    FLASK_APP = 'flask_app'

    def __init__(self, json_value):
        self.json_value = json_value


@enum.unique
class PythonVersion(enum.Enum):
    """
    Enumeration of supported nicknames for python versions
    Used through out the makefiles in the emitted template
    """

    V27 = ("py27", "python2.7")
    V34 = ("py34", "python3.4")
    V35 = ("py35", "python3.5")

    def __init__(self, nickname, executable_name):
        self.nickname = nickname
        self.executable_name = executable_name

    @staticmethod
    def get_python2_versions():
        return tuple([PythonVersion.V27])

    @staticmethod
    def get_python3_versions():
        return tuple([PythonVersion.V34, PythonVersion.V35])


@enum.unique
class PythonVersionMode(enum.Enum):
    """
    Enumeration of supported values for `cookiecutter.python_version_mode`
    Ordered by default first.
    """

    PY27_ONLY = ('py27_only', tuple([PythonVersion.V27]))
    PY27_THRU_PY3 = ('py27_thru_py3', tuple(PythonVersion))
    PY3_ONLY = ('py3_only', PythonVersion.get_python3_versions())

    def __init__(self, json_value, py_versions):
        self.json_value = json_value
        self.python_versions = py_versions


@enum.unique
class PythonRepoMode(enum.Enum):
    """
    Enumeration of the supported values for `cookiecutter.python_repo_mode`
    Ordered by default first.
    """

    MIRRORED_AND_INTERNAL = 'mirrored_and_internal'
    PUBLIC_ONLY = 'public_only'

    def __init__(self, json_value):
        self.json_value = json_value


@enum.unique
class VagrantBoxMode(enum.Enum):
    """
    Enumeration of the supported values for `cookiecutter.vagrant_box_mode`
    Ordered by default first.
    """

    INTERNAL_ONLY = 'internal_only'
    PUBLIC_ONLY = 'public_only'

    def __init__(self, json_value):
        self.json_value = json_value


@enum.unique
class DependencyManagementMode(enum.Enum):
    """
    Enumeration of the supported values for `cookiecutter.dependency_management_mode`
    Ordered by default first.
    """

    MANAGED_IN_HOUSE = ('managed_in_house', PythonRepoMode.MIRRORED_AND_INTERNAL, VagrantBoxMode.INTERNAL_ONLY)
    PUBLIC_THIRD_PARTIES = ('public_third_parties', PythonRepoMode.PUBLIC_ONLY, VagrantBoxMode.PUBLIC_ONLY)

    def __init__(self, json_value, python_repo_mode, vagrant_box_mode):
        self.json_value = json_value
        self.python_repo_mode = python_repo_mode
        self.vagrant_box_mode = vagrant_box_mode


@enum.unique
class VagrantVMRole(enum.Enum):
    """Enumeration of roles for the vagrant vm"""

    BUILD = 1
    SYSTEM_TEST = 2


@enum.unique
class VagrantVM(enum.Enum):
    """Enumeration of expected VMs in the Vagrant env of the emitted project"""

    BUILD_VM = ("build_vm", VagrantVMRole.BUILD)
    SYSTEM_TEST_VM = ("sys_test_vm", VagrantVMRole.SYSTEM_TEST)

    def __init__(self, vm_name, vm_role):
        self.vm_name = vm_name
        self.vm_role = vm_role

    def get_status_cmd(self):
        return 'status {}'.format(self.vm_name)

    def get_destroy_cmd(self):
        return 'destroy -f {}'.format(self.vm_name)

    def get_up_cmd(self):
        return 'up {}'.format(self.vm_name)

    def get_ssh_cmd(self, ssh_command):
        return 'ssh {} -c "{}"'.format(self.vm_name, ssh_command)


@enum.unique
class PipRequirementsFile(enum.Enum):
    """Enumeration of pip requirements files that should be in the emitted project"""

    DEV_REQUIREMENTS_TXT = ("dev-requirements.txt")
    REQUIREMENTS_TXT = ("requirements.txt")

    def __init__(self, file_name):
        self.file_name = file_name


@enum.unique
class TravisLanguage(enum.Enum):

    PYTHON = ('python')

    def __init__(self, field_value):
        self.field_value = field_value


@enum.unique
class ECTravisLanguage(enum.Enum):

    DEB_1404 = ('deb1404')
    DEB_1604 = ('deb1604')

    def __init__(self, field_value):
        self.field_value = field_value

