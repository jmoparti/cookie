"""
Pre-processing hooks used by cookiecutter
"""

#
# Imports
#

# core python
from __future__ import print_function
import logging
import re
import sys


#
# Module variables
#

_LOGGER = logging.getLogger('pre_gen_project')

#
# Hook implementation
#

def assert_not_empty(text):
    """Asserts text is not empty string"""
    assert text, "was empty string"
    return text


def assert_not_all_whitespace(text):
    """Asserts text doesn't consist entirely of whitespace"""
    assert text.strip(), "was entirely whitespace"
    return text


def validate_cookiecutter_params():
    """Validate the cookiecutter params"""

    # author name
    author_name = '{{cookiecutter.author_name}}'
    assert_not_all_whitespace(assert_not_empty(author_name))

    # author email
    author_email = '{{cookiecutter.author_email}}'
    assert_not_all_whitespace(assert_not_empty(author_email))

    # company name
    company_name = '{{cookiecutter.company_name}}'
    assert_not_all_whitespace(assert_not_empty(company_name))

    # copyright year
    copyright_year = '{{cookiecutter.copyright_year}}'
    assert re.match(r'^[0-9]{4}$', copyright_year) is not None, "was not 4 digit year"

    dependency_management_mode = '{{cookiecutter.dependency_management_mode}}'
    assert dependency_management_mode in ["managed_in_house", "public_third_parties"], \
        "Not one of the allowed choices"

    package_name = '{{cookiecutter.package_name}}'
    assert re.match(r'^[a-zA-Z0-9-]+$', package_name) is not None, \
        "Hyphen is only allowed special character, rest must be alphanumerical"

    package_version = '{{cookiecutter.package_version}}'
    assert_not_all_whitespace(assert_not_empty(package_version))

    project_flavor = '{{cookiecutter.project_flavor}}'
    assert project_flavor in ['bare_bones', 'library', 'cli_app', 'flask_app'], \
        "Not one of the allowed choices"

    project_name = '{{cookiecutter.project_name}}'
    assert_not_all_whitespace(assert_not_empty(project_name))

    project_short_description = '{{cookiecutter.project_short_description}}'
    assert_not_all_whitespace(assert_not_empty(project_short_description))

    python_version_mode = '{{cookiecutter.python_version_mode}}'
    assert python_version_mode in ['py27_only', 'py27_thru_py3', 'py3_only' ], \
        "Not one of the allowed choices"

    root_module_name = '{{cookiecutter.root_module_name}}'
    assert re.match(r'^[a-z0-9_]+$', root_module_name) is not None, \
        "Underscore is only allowed special character, rest must be lower-case alphanumerical"


def run_hook():
    """Run the hook itself"""
    try:
        validate_cookiecutter_params()
    except Exception:
        _LOGGER.exception("Pre-gen hook raised fatal error")
        sys.exit(1)
    else:
        sys.exit(0)

#
# Now run it
#

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    run_hook()
