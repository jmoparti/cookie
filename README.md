# cookiecutter-sysops-python-package

## Introduction

This is a [Cookiecutter template](https://github.com/audreyr/cookiecutter) for SysOps/SI Python package projects.

## Goals

The templates emit lowest-common denominator `opinionated` baselines for Python package project structures.

* The intent is to have a single parameterized cookiecutter template for the more common of kinds of Python package projects, rather than having
  multiple special purpose cookiecutter templates.
* The resultant projects *can* be tailored to meet the specific needs of their end-users, as long as they
  stay within the spirit of repeatable, consistent builds and installs.
* The point is to get Python packages that can be repeatably built, tested, documented, and installed.

For example:

* Instead of maintaining a separate cookiecutter for Python 2.7 projects vs Python 3.5 etc, just maintain one cookiecutter with optional flags
  to allow choosing with Python interpreter versions you want supported in the project created by the template.
* Instead of maintaining a separate cookiecutter for projects we want to open source versus ones that are only in-house, just maintain one
  cookiecutter with optional flags to indicate public vs private repos and public vs. private vagrant boxes.

## See Also

* [How to use this project](USAGE.md)
* [How to contribute to this project](CONTRIBUTING.md)
* [This repo's wiki](https://git.edgecastcdn.net/SysOps/cookiecutter-sysops-python-package/wiki)
  * [FAQ](https://git.edgecastcdn.net/SysOps/cookiecutter-sysops-python-package/wiki/FAQ)

## History

* This is a replacement for the [first generation template](https://git.edgecastcdn.net/sysops-eol/cookiecutter-sysops-py27-package).
* This epic in JIRA is used to track bug/feature todos: [SI-1270](https://ecjira.atlassian.net/browse/SI-1270).
