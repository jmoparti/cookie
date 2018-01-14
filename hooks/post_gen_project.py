"""
Post-processing hooks used by cookiecutter
"""

#
# Imports
#

# core python
from __future__ import print_function
import ast
import datetime
import json
import logging
import os
import platform
import shutil
import sys

#
# Module variables
#

_LOGGER = logging.getLogger('post_gen_project')


#
# Hook implementation
#

def _delete_file_or_dir(relative_path):
    """Deletes a file or dir"""
    path = os.path.join(os.getcwd(), relative_path)
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
    else:
        os.unlink(path)


def tailor_based_on_py_version_mode():
    """Based on the Python interpreter version(s) supported, tailor the project that was emitted"""

    # get the python version mode from the cookiecutter plumbing
    python_version_mode = '{{cookiecutter.python_version_mode}}'

    # get hit list based on it
    relative_paths_to_remove = []
    if python_version_mode == 'py27_only':
        # no-op for now
        pass
    elif python_version_mode == 'py3_only':
        # no-op for now
        pass
    elif python_version_mode == 'py27_thru_py3':
        # no-op for now
        pass
    else:
        raise Exception(
            "cookiecutter.python_version_mode had unsupported value: '{}'".format(
            '{{cookiecutter.python_version_mode}}'))

    # walk hit list and delete
    for relative_path in relative_paths_to_remove:
        _delete_file_or_dir(relative_path)


def _copy_dir_recursively(relative_source_path, relative_destination_path):
    """
    Copies a directory recursively.

    Had to implement this because ``shutil.copy`` doesn't allow copying to an existing directory.  sigh.
    """
    _LOGGER.debug("Recursively copying from %s to %s", relative_source_path, relative_destination_path)
    _LOGGER.debug("In current working directory: %s", os.getcwd())
    root_src_dir_path = os.path.join(os.getcwd(), relative_source_path)
    root_dst_dir_path = os.path.join(os.getcwd(), relative_destination_path)
    assert os.path.exists(root_src_dir_path), "root source directory doesn't exist: {}".format(root_src_dir_path)
    assert os.path.exists(root_dst_dir_path), "root destination directory doesn't exist: {}".format(root_dst_dir_path)

    for src_dir_path, src_dir_name, src_file_names in os.walk(root_src_dir_path):
        dst_dir_path = src_dir_path.replace(root_src_dir_path, root_dst_dir_path, 1)
        if not os.path.exists(dst_dir_path):
            os.makedirs(dst_dir_path)
        for src_file_name in src_file_names:
            src_file_path = os.path.join(src_dir_path, src_file_name)
            assert os.path.exists(src_file_path), "source file path doesn't exist: {}".format(src_file_path)
            shutil.copy2(src_file_path, dst_dir_path)


def tailor_based_on_project_flavor():
    """Based on the choosen project 'flavor', tailor the project that was emitted"""

    # get the project flavor the cookiecutter plumbing
    root_origin_path = 'cookiecutter-project-flavors'
    project_flavor = '{{cookiecutter.project_flavor}}'

    # identify the base path for where you're copying to
    base_origin_path = os.path.join(root_origin_path, project_flavor)
    root_module_name = '{{cookiecutter.root_module_name}}'
    src_to_dst = {
        os.path.join(base_origin_path, root_module_name): root_module_name,
        os.path.join(base_origin_path, 'tests'): 'tests',
        os.path.join(base_origin_path, 'sphinx_docs'): 'sphinx_docs',
        os.path.join(base_origin_path, 'vagrant'): 'vagrant',
    }
    for relative_src_path, relative_dst_path in src_to_dst.items():
        if os.path.exists(relative_src_path):
            _copy_dir_recursively(relative_src_path, relative_dst_path)

    # now remove the original staging area
    _LOGGER.debug("Now removing the base source path for staged assets: %s", root_origin_path)
    shutil.rmtree(root_origin_path)


def capture_cookiecutter_params():
    """Capture cookiecutter parameters"""

    # use literal eval to keep pylint from chocking on jinja template
    data = ast.literal_eval('''
{
{% for key, value in cookiecutter.items() %}
    "{{key}}": "{{value}}",
{% endfor %}
}
''')
    return data


def write_breadcrumb_file(path):
    """
    Write out the breadcrumb file which will contain the cookiecutter settings etc. used to
    generate the project structure.
    """

    # capture cookiecutter parameters
    cookiecutter_params = capture_cookiecutter_params()

    # get runtime env info
    runtime_env = {
        'python_version': platform.python_version(),
        'platform': platform.platform(),
        'current_time': datetime.datetime.now().isoformat(),
    }

    # fill in total json data
    json_data = {
        'cookiecutter_params': cookiecutter_params,
        'runtime_env': runtime_env,
    }

    # write it out
    with open(path, 'w') as json_file:
        json.dump(json_data, json_file, indent=4, sort_keys=True)


def run_hook():
    """The hook itself"""
    try:
        # do tailoring
        tailor_based_on_py_version_mode()
        tailor_based_on_project_flavor()

        # write out breadcrumb file
        path = 'cookiecutter-crumbs.json'
        write_breadcrumb_file(path)
    except Exception:
        _LOGGER.exception("Post gen hook raised fatal error")
        sys.exit(1)
    else:
        # exit clean if all good
        sys.exit(0)

#
# Now run it
#

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    run_hook()
