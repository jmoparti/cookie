*********************************************************
Contributing to the {{cookiecutter.project_name}} Project
*********************************************************

.. todo::

    This document should provide at least a high level description of the following concerns
    for potential contributors:

    * How is the project governed?
        * Who are the maintainers/referees?  And how do you contact them?
    * What is the change management process?
        * Pull request workflow
        * JIRA workflow
    * What is the basic build and test process?
    * What are the project specific practices?
        * Which version of Python is targeted?
        * What OS (and architecture) is targeted ?
        * General code style

    Where necessary, you can link to other documents for more in-depth walk throughs of the
    above concerns.

    Below is a starter skeleton based loosely off of Flask's contributing howto.

----

Building and Testing
====================

.. todo::

    * How does someone get the source code?
    * What are the build procedures (both automated and manual)?
    * What are the test procedures (both automated and manual)?
    * Is there any continuous integration available?

Getting the source
------------------

.. todo::

    Write up how someone would get access to the source code.
    e.g. go to a GitHub repo etc.

Running builds and tests
------------------------

Overview
^^^^^^^^

Architecture
~~~~~~~~~~~~

This project leverages a layer cake of Python ecosystem build tools:

.. code-block:: text

    |-----------------|
    |      Make       | { provides coarse grain build/test steps
    |-----------------|
             |
             V
    |-----------------|
    |      tox        | { sets up virtualenv and picks Python interpreter
    |-----------------|
             |
             V
    |-----------------|
    |    setuptools   | { provides fine grain build/test steps
    |-----------------|


* The foundational layer is driven via `setuptools`.
    * This layer is used for basic Python build and test tasks
* The next layer up is `tox`
    * The primary responsibility of this layer is to manage isolated
      sandboxes representing specific Python interpreter versions
      and external dependencies.
    * Basic tasks are delegated to `setuptools`
* The topmost layer is a `Makefile` for use with `make`
    * This layer is responsible for definining high level tasks, like
      "build me a wheel file", and delegates to `tox` and `setuptools`
      for the basic tasks needed for that.

Building
~~~~~~~~

The project is intended to be distributed as a ``wheel``.

Use the included ``wheel`` Makefile target to build this project's deliverable wheel.  It
will end up in `dist/`.

Testing
~~~~~~~

This project provides the following to help you test your work:

* Pylint
    * Run ``make lint``
* Pytest with support for test coverage metrics and detailed test reporting
    * For the basic testing of unit & integration & system tests with terminal reporting: ``make tests``
    * For detailed html reports for coverage and test success for:
        * just unit tests ``make unit_tests``
        * just integration tests ``make integration_tests``
        * just system tests ``make system_tests``

Read the Makefile for more details.

Makefile Usage
^^^^^^^^^^^^^^

Run the default Make targets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default Make targets are the following (in order of how they are run):

* clean
* build
* lint
* lint_tests
* tests
* docs
* wheel

You can run them like this:

.. code-block:: shell

    cd <repo>
    make

or

.. code-block:: shell

    cd <repo>
    make all

Optional Make targets
~~~~~~~~~~~~~~~~~~~~~

Several optional Make targets are provided:

* docs_draft
* unit_tests
* int_tests
* system_tests
* format_with_yapf
* test_wheel

Please read the inline comments in the Makefile itself for details on what they are and what they do.

Picking which Tox Python to use
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Normally the variables already declared in the `Makefile` will stipulate which Python environments
are used by `tox` as it runs `setuptools` on your behalf when you kick it all off via Make.

However, sometimes you might want to change that temporarily. In those cases, you can pass the `TOXENV` variable as an option to the Make command line.

The makefile targets run commands that respect the `TOXENV` [shell environment variable for stipulating which Python environments will be used](https://tox.readthedocs.io/en/latest/config.html#confval-envlist=CSV).

For example, if you wanted to run the lint, but only with Python 3.4, you could do the following:

.. code-block:: shell

    cd <repo>
    make TOXENV=py34 lint


Ad-Hoc Usage
^^^^^^^^^^^^

Aside from the canned tests above, you can stand up a development bubble and poke around.

The setuptools ``develop`` command will setup the fundamental bubble.  The Makefile has
targets that will run the setuptools ``develop`` command within the context of a ``tox``
managed ``virtualenv``.

Below is an example of an ad-hoc session:

.. code-block:: shell

   cd <repo>
   # stand up the setuptools develop bubble
   make develop

   # activate a virtualenv managed by tox
   source .tox/<your-py-env>/bin/activate

{%- if cookiecutter.project_flavor == 'cli_app' %}
   # Run the command line script
   python -m {{cookiecutter.root_module_name}}.cli
{%- elif cookiecutter.project_flavor == 'flask_app' %}
   # Use the flask package's cli scaffolding to run a debug instance of the web app
   export FLASK_APP={{cookiecutter.root_module_name}}.uwsgi
   export FLASK_DEBUG=1
   flask run
{% else %}
   # Do a python import of the root module
   python -c "import {{cookiecutter.root_module_name}}"

   # Launch a python interpreter session and you'll be able to import there too
   python
{%- endif %}


Additional Resources
^^^^^^^^^^^^^^^^^^^^

The included Vagrant environment, which has:

* ``build_vm`` -- a cleanroom build VM
* ``sys_test_vm`` -- a cleanroom VM that can be used as a guinea pig for system testing

----

Support Questions
=================

.. todo::

    * Who is the point of contact for support?
    * What are the preferred methods of contacting them?  Slack? Carrier Pidgeon?

-----

Reporting Issues
================

.. todo::

    * What issue tracking is preferred? JIRA?  GitHub issues?
    * What details should be included, other than the obvious?

----

Proposing Changes
=================

.. todo::

    * Who are the referee/maintainers responsible for vetting proposed changes?
    * What is the process for submitting those changes for review?
