# Usage

This project is a template for use with the [Cookiecutter tool](https://github.com/audreyr/cookiecutter).

It is intended to assist in standing up SysOps/SI Python package projects.


## Pre-requisites

> **CAVEAT**
>
> These are pre-requisites for the use of `cookiecutter` to generate projects, and this is **NOT**
> the list of prerequisites needed by the generated projects themselves.

* Supported host operating systems
    * Unix-like (Ubuntu, Mac OS)
    * **Windows is NOT supported**
* Python platform
    * Minimum Python interpreter version is `2.7`
        * NOTE: This is the minimum version of Python required to **run** the `cookiecutter` tool itself.
          This is **NOT** the minimum version of Python required to run whatever is in the project emitted
          by `cookiecutter` using the template in this repository.
* A virtualenv or system Python package environment with the following Python packages installed to it:
  * `cookiecutter`
    * Tested with cookiecutter version ``1.6.0``

## Using the cookiecutter command line

### Examples

All these examples assume that you want to pull from the 'master' branch.

Using the default settings (only suggested for trying it out, not for 'real' use).

```
mkdir temp
cd temp
cookiecutter --no-input --checkout master https://git.edgecastcdn.net/sysops/cookiecutter-sysops-python-package.git
```

Using the 'prompt me' mode to allow you to customize the settings.

```
mkdir temp
cd temp
cookiecutter --checkout master https://git.edgecastcdn.net/sysops/cookiecutter-sysops-python-package.git
```

## Using the cookiecutter Python API

The `cookiecutter` package has a Python API as well as the executable.

You can use it to have non-default settings without having to type them at the command line prompts from the `cookiecutter` command line script.

### Examples

Below is an example of a Python snippet that calls the cookiecutter Python API with custom settings.

```
import cookiecutter.main

git_repo_url = 'https://git.edgecastcdn.net/sysops/cookiecutter-sysops-python-package.git'
your_overrides = {
    'project_name': 'My Special Project',
    'package_name': 'my-special-project',
    'root_module_name': 'my_special_project',
}
cookiecutter.main.cookiecutter(git_repo_url, checkout='master', extra_context=your_overrides)
```

## Configuration

### Cookiecutter JSON

The `cookiecutter.json` file at the root of the repository sets the defaults and available choices for the template's user-facing variables.

Variable Name               | Purpose
----------------------------|-----------------------------------------------------------------------------------------------------------------------|
`author_name`               | Author(s) name.  Used in project's docs and Python package meta-data.
`author_email`              | Email address for containg the Author(s).  Used in project's docs and Python package meta-data.
`company_name`              | Company name.  Used in project's docs and Python package meta-data.
`copyright_year`            | Copyright year for the project.  Used in the project's docs and Python package meta-data.
`dependency_management_mode` | Multiple choice variable to select what flavor of dependencies (python repos, vagrant boxes etc.) to leverage in the emitted project.
`package_name`              | Name of the Python `distribution package` emitted by the project.
`package_version`           | The version value for the Python `distribution package` emitted by the project.
`project_flavor`            | The "flavor" of project to emit.  e.g. bare bones skeleton, library, command line application.
`project_name`              | Human readable project name.  For use in docs and Python package meta-data.
`project_short_description` | Short, human readable description of the project.  For use in docs and Python package meta-data
`python_version_mode`       | Multiple choice variable to select what range of Python versions to support.
`root_module_name`          | Root level module name for the project's code-base.  Should be similar to the `package_name` but doesn't have to be identical.

Variable Name               | Default value
----------------------------|-----------------------------------------------------------------------------------------------------------------------|
`author_name`               | `SysOps`
`author_email`              | `sysops@verizondigitalmedia.com`
`company_name`              | `EdgeCast/VDMS`
`copyright_year`            | `2017`
`dependency_management_mode` | `managed_in_house`
`package_name`              | `sysops-boilerplate`
`package_version`           | `0.1.0`
`project_flavor`            | `bare_bones`
`project_name`              | `SysOps Boilerplate`
`project_short_description` | `Boilerplate Python project using SysOps conventions`,
`python_version_mode`       | `py27_only`
`root_module_name`          | `so_boilerplate`

Variable Name               | Allowed values
----------------------------|-----------------------------------------------------------------------------------------------------------------------|
`author_name`               | Text that is not completely whitespace.
`author_email`              | Valid email address.
`company_name`              | Text that is not completely whitespace.
`copyright_year`            | A 4 digit representation of a year.  e.g. `2017`
`dependency_management_mode` | One of the following values: `managed_in_house` (default), `public_third_parties`
`package_name`              | Should be all lower-case, no spaces, and no underscores.  Use hyphens instead of spaces or underscores.
`package_version`           | Follow [PEP 440](https://www.python.org/dev/peps/pep-0440/).
`project_flavor`            | One of the following values: `bare_bones` (default), `library`, `cli_app`, `flask_app`
`project_name`              | Text that is not completely whitespace.
`project_short_description` | Text that is not completely whitespace.
`python_version_mode`       | One of the following values: `py27_only` (default), `py27_thru_py3`, `py3_only`
`root_module_name`          | Should be all lower-case, no spaces, and no hypthens.  Use underscores instead of spaces or hypens.

Further explanation of "choice" variables:

* `dependency_management_mode`
  * `managed_in_house` (default choice)
    * Python repositories
      * Use our in-house mirror of PyPI for the primary Python package repository (aka "index url" in pip terminology)
      * Use our in-house ad-hoc repository as the "extra" package repository (aka "extra index url" in pip terminology)
    * Vagrant boxes
      * Only use our in-house Vagrant box images.
  * `public_third_parties`
    * Python repositories
      * Only use PyPI as the project's Python package repository.
    * Vagrant boxes
      * Only use publicly available Vagrant box images.
* `project_flavor`
  * `bare_bones` (default)
    * A bare bones project skeleton.
    * Makes the minimum assumptions.
  * `library`
    * Skeleton for a shared Python library.
    * Has a "starter" sphinx docs page that uses the sphinx autodoc feature to emit public api docs.
  * `cli_app`
    * Skeleton for a command line app using only "stock" Python.  e.g. no `click`
    * Has a stubbed out command line entry point that
        * uses `argparse` to parse command line arguments
        * adjusts log levels based on optional flags at the command line
        * aside from those features, it is a runnable no-op
  * `flask_app`
    * Skeleton for a basic Flask web application.
    * Has stubs and hooks for basic stuff like `uwsgi` integration
    * Has a system test Vagrant VM with provisioning logic to stand up a `nginx+uwsgi+flask` environment
* `python_version_mode`
  * `py27_only` (default choice)
    * Only support Python 2.7
  * `py27_thru_py3`
    * Support Python 2.7, and 3.x
  * `py3_only`
    * Only support Python 3.x

## See Also

* [This repo's README.md](README.md)
* [This repo's CONTRIBUTING.md](CONTRIBUTING.md)
* [This repo's wiki](https://git.edgecastcdn.net/SysOps/cookiecutter-sysops-python-package/wiki)
