# -*- coding: utf-8 -*-
"""
Utilities for cookiecutter JSON and invocation
"""

#
# Imports
#

# import core
import collections
import copy
import logging
import os

# import third party
import cookiecutter
import cookiecutter.main
import enum
import marshmallow

# this project
from tests.constants import (
    DependencyManagementMode,
    ProjectFlavor,
    PythonRepoMode,
    PythonVersionMode,
    VagrantBoxMode,
)
from tests.common.misc_utils import (
    redirected_stdout_and_stderr,
    run_shell,
)

#
# Module variables
#

# logger
_LOGGER = logging.getLogger(__name__)


#
# Classes for invoking cookiecutter cli
#

class CookieCutterInvoker(object):
    """Wrapper around invocations to cookiecutter via api/cli"""

    def __init__(self, repo_root_path, cookiecutter_config_path):
        assert os.path.exists(repo_root_path), \
            "repo root path does not exist: {}".format(repo_root_path)
        self.repo_root_path = repo_root_path
        assert os.path.exists(cookiecutter_config_path), \
            "cookiecutter config path does not exist: {}".format(cookiecutter_config_path)
        self.cookiecutter_config_path = cookiecutter_config_path

    def invoke_via_api(self, root_output_path, extra_context=None):
        """Run cookiecutter template via its Python API"""
        run_params = locals()
        _LOGGER.info("Begin calling cookiecutter API with template under test: %s", run_params)

        try:
            with redirected_stdout_and_stderr():
                cookiecutter.main.cookiecutter(
                    template=self.repo_root_path,
                    no_input=True,
                    output_dir=root_output_path,
                    overwrite_if_exists=False,
                    config_file=self.cookiecutter_config_path,
                    extra_context=extra_context)
        except Exception as error:
            _LOGGER.exception("Call to cookiecutter API failed")
            raise Exception("Cookiecutter failed, see log file")
        else:
            _LOGGER.info("Finished calling cookiecutter API with template under test: %s",
                         run_params)

    def invoke_via_cli(self, working_path, root_output_path):
        """Run cookiecutter template via its command line interface"""
        run_params = locals()
        _LOGGER.info("Begin calling cookiecutter CLI with template under test: %s", run_params)

        try:
            cmd_text = ' '.join([
                'cookiecutter',
                '--no-input',
                '--config-file',
                self.cookiecutter_config_path,
                '--output-dir',
                root_output_path,
                self.repo_root_path,
            ])
            run_shell(cmd_text, working_path=working_path)
        except Exception as error:
            _LOGGER.exception("Call to cookiecutter CLI failed")
            raise Exception("Cookiecutter failed, see log file")
        else:
            _LOGGER.info("Finished calling cookiecutter CLI with template under test: %s",
                         run_params)

#
# Enums and classes for cookiecutter JSON
#

@enum.unique
class CookiecutterJSONField(enum.Enum):
    """Enumeration of supported fields in cookiecutter.json"""

    AUTHOR_NAME = ("author_name", None)
    AUTHOR_EMAIL = ("author_email", None)
    COMPANY_NAME = ("company_name", None)
    COPYRIGHT_YEAR = ("copyright_year", None)
    DEPENDENCY_MANAGEMENT_MODE = ("dependency_management_mode", DependencyManagementMode)
    PACKAGE_NAME = ("package_name", None)
    PACKAGE_VERSION = ("package_version", None)
    PROJECT_FLAVOR = ("project_flavor", ProjectFlavor)
    PROJECT_NAME = ("project_name", None)
    PROJECT_SHORT_DESCRIPTION = ("project_short_description", None)
    PYTHON_VERSION_MODE = ("python_version_mode", PythonVersionMode)
    ROOT_MODULE_NAME = ("root_module_name", None)

    def __init__(self, json_name, choices_enum):
        self.json_name = json_name
        self.choices_enum = choices_enum

    def get_available_choices(self):
        """Return available choices if any"""
        if not self.choices_enum:
            raise Exception("This enum doesn't have choices: {}".format(self))
        return [item.json_value for item in tuple(self.choices_enum)]


class CookiecutterJSONSchema(marshmallow.Schema):
    """Schema for the cookiecutter.json data"""

    @staticmethod
    def raise_if_invalid(data):
        """Raise exception if data fails schema validation"""
        schema = CookiecutterJSONSchema(strict=True)
        errors = schema.validate(data)
        if errors:
            raise Exception("Data failed schema validation: {}".format(errors))

    @staticmethod
    def _create_validator_fn_for_choices_field(field_enum):
        """Builds an anonymous function to validate based on the field enum"""
        if not field_enum.choices_enum:
            raise Exception("Unsupported field enum: {}".format(field_enum))
        def anon_fn(field_value):
            # extract some essentials
            avail_choices = field_enum.get_available_choices()

            # now validate that the list of actual values matches list of expected
            if field_value != avail_choices:
                raise marshmallow.ValidationError(
                    "Field {} has value(s) '{}' that do not match the expected available "
                    "choices: {}".format(field_enum.json_name, field_value, avail_choices))
        return anon_fn

    def __init__(self, **kwargs):
        for field_enum in iter(CookiecutterJSONField):
            field_name = field_enum.json_name
            if field_enum.choices_enum:
                validate_fn = CookiecutterJSONSchema._create_validator_fn_for_choices_field(
                    field_enum)
                schema_field = marshmallow.fields.List(
                    marshmallow.fields.String(validate=validate_fn),
                    attribute=field_name,
                    required=True)
            else:
                schema_field = marshmallow.fields.String(attribute=field_name, required=True)
            self.__setattr__(field_enum.json_name, schema_field)
        self.ordered = True
        super(CookiecutterJSONSchema, self).__init__(**kwargs)


class CookiecutterExtraContextSchema(marshmallow.Schema):
    """Schema for the cookiecutter 'extra context' data passed via its Python API"""

    @staticmethod
    def raise_if_invalid(data):
        """Raise exception if data fails schema validation"""
        schema = CookiecutterExtraContextSchema(strict=True)
        errors = schema.validate(data)
        if errors:
            raise Exception("Data failed schema validation: {}".format(errors))

    @staticmethod
    def _create_validator_fn_for_choices_field(field_enum):
        """Builds an anonymous function to validate based on the field enum"""
        if not field_enum.choices_enum:
            raise Exception("Unsupported field enum: {}".format(field_enum))
        def anon_fn(field_value):
            # extract some essentials
            avail_choices = field_enum.get_available_choices()

            # now validate that the list of actual values matches list of expected
            if field_value not in avail_choices:
                raise marshmallow.ValidationError(
                    "Field {} has value '{}' that is not in the available choices: {}".format(
                        field_enum.json_name, field_value, avail_choices))
        return anon_fn

    def __init__(self, **kwargs):
        for field_enum in iter(CookiecutterJSONField):
            field_name = field_enum.json_name
            if field_enum.choices_enum:
                validate_fn = CookiecutterExtraContextSchema._create_validator_fn_for_choices_field(
                    field_enum)
                schema_field = marshmallow.fields.String(
                    attribute=field_name,
                    required=True,
                    validate=validate_fn)
            else:
                schema_field = marshmallow.fields.String(attribute=field_name, required=True)
            self.__setattr__(field_enum.json_name, schema_field)
        self.ordered = True
        super(CookiecutterExtraContextSchema, self).__init__(**kwargs)


class CookiecutterExtraContextBuilder(object):
    """Builder for cookiecutter 'extra context' datasets"""

    def __init__(self):
        self.schema = CookiecutterExtraContextSchema(strict=True)

    def build_from_cookiecutter_json(self, json_data):
        """Build an extra context instance from cookiecutter.json"""
        _LOGGER.debug("Begin building extra context from cookiecutter.json")
        CookiecutterJSONSchema.raise_if_invalid(json_data)
        extra_context = {}
        for field_enum in tuple(CookiecutterJSONField):
            field_name = field_enum.json_name
            if field_enum.choices_enum:
                extra_context[field_name] = json_data[field_name][0]
            else:
                extra_context[field_name] = json_data[field_name]
        self.schema.validate(extra_context)
        _LOGGER.debug("Built extra context: %s", extra_context)
        _LOGGER.debug("Finished building extra context from cookiecutter.json")
        return extra_context

    def update(self, extra_context, field_enum, field_value):
        """Update an existing extra context instance based on the field enum and value"""
        _LOGGER.debug("Begin updating extra context dict based on field enum")
        _LOGGER.debug("Original extra context dict is %s", extra_context)
        self.schema.validate(extra_context)
        assert isinstance(field_enum, CookiecutterJSONField)
        assert isinstance(field_value, str), \
            "value for field {} was not str type: '{}'".format(field_enum, field_value)
        extra_context[field_enum.json_name] = field_value
        self.schema.validate(extra_context)
        _LOGGER.debug("Updated extra context dict is %s", extra_context)
        _LOGGER.debug("Finished updating extra context dict based on field enum")

    def build_from_json_and_test_params(self, cookiecutter_json_data, specific_test_params):
        """Build using a baseline of cookiecutter json data updated by specific test params"""
        _LOGGER.debug("Begin building based on both cookiecutter.json and specific test params")

        # verify the specific test params as being a named tuple of some kind
        _LOGGER.debug("Using specific test params: %s", specific_test_params)
        assert isinstance(specific_test_params, tuple)

        # create the base context based off the json obj
        builder = CookiecutterExtraContextBuilder()
        extra_context = builder.build_from_cookiecutter_json(cookiecutter_json_data)

        # now update it
        for field_enum in tuple(CookiecutterJSONField):
            field_name = field_enum.json_name
            if hasattr(specific_test_params, field_name):
                field_value = getattr(specific_test_params, field_name, None)
                assert field_value is not None
                self.update(extra_context, field_enum, field_value.json_value)

        _LOGGER.debug("Finished building based on both cookiecutter.json and specific test params")
        return extra_context

