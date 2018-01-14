# Automated testing

----

## Overview

The test harness for this project is implemented via Make and `pytest`.

The Makefile included in this directory (`<repo>/testing`) has targets that run various test scenarios with
this cookiecutter template.

You can run the test harness in one of these environments:

* On your local machine
  * Directly on the machine
  * In the provided Vagrant environment
    * Note that tests which require VirtualBox will *not* run in this kind of remote VM right now. (see below for details)
* On a remote VM
  * In the Spetsnaz OpenStack cluster
    * See below for a recipe for this
    * Note that tests which require VirtualBox will *not* run in this kind of remote VM right now. (see below for details)
  * Some other VM somewhere
    * This is your problem, no recipe is provided.

----

## General Usage

Regardless of where you are running the tests, the same Makefile targets are used.

For the rest of these examples, only the "raw" ``make`` command
line will be described and not whether or not you are running it on
your host or inside the included Vagrant environment.

For full details, please familiarize yourself with [the Makefile that runs the tests in harness](Makefile).

Below are usage examples for several of the more common use-cases.

### Running pylint

Run pylint on the test harness itself:

```
cd <repo>/testing
make lint_self
```

Run pylint on the ["hook" scripts](../hooks) used in the cookiecutter template itself:

```
cd <repo>/testing
make lint_hooks
```

**Run the template locally without the test harness**

Run it with prompts for inputs:

```
cd <repo>/testing
make run_cookiecutter_with_input
```

Run it without prompts for inputs:

```
cd <repo/testing
make run_cookiecutter_wout_input
```

### Testing the makefile targets in the emitted project

**Using the ``cookiecutter`` tool's Python API to invoke the template creation**

Run all possible API tests:

```
cd <repo>/testing
make test_make_via_api
```

Run a filtered subset of all possible API tests:

```
# Only run tests related Python2.7 only projects
> make PYTEST_ADDOPTS="--only-python-version-mode py27_only" clean test_make_via_api

# see the full list available
> .virtualenv/bin/py.test --help
...
custom options:
  --only-dependency-management-mode={managed_in_house,public_third_parties}
                        Override dependency management mode used in tests
  --only-make-target={all,build,clean,clean_all,combined_tests,develop,docs,docs_draft,format_with_yapf,lint,test_wheel,tests,wheel}
                        Override the make targets used in tests
  --only-project-flavor={bare_bones,cli_app,flask_app,library}
                        Override project flavor used in tests
  --only-python-version-mode={py27_only,py27_thru_py35,py34_thru_py35,py35_only}
                        Override python version mode used in tests
```

>
> NOTE: those filters only apply to tests via the Python API right now
>

**Using the ``cookiecutter`` tool's command line interface to invoke the template creation**

Run all possible cli tests:

```
cd <repo>/testing
make test_make_via_cli
```

Testing both Python API and CLI invocations:

```
cd <repo>/testing
make test_make
```

### Testing the Vagrant environment in the emitted project

Test the "build" vm included in the emitted project's Vagrant environment:

```
cd <repo>/testing
make test_vagrant_build_vm
```

Test the "system test" vm included in the emitted project's Vagrant environment:

```
cd <repo>/testing
make test_vagrant_sys_test_vm
```

Test all the VMs included in the emitted project's Vagrant environment:

```
cd <repo>/testing
make test_vagrant_env
```

Test just the travis environment stuff in the emitted projects 
(note this only does a light set of testing, see [the manual tests doc](MANUAL_TESTS.md) for more details):

```
cd <repo>/testing
make test_travis_env
```

### Run all possible tests

```
cd <repo>/testing
make all
```

----

## Running directly on your local host

### Prerequisites

Your host machine must have the following:

* A Unix-like operating system (Linux, Mac OS).
  * Windows is *not* supported.
* Have the following non-pythonic tools installed:
  * Vagrant version 1.8.5 or above
  * Virtualbox version 5.1 or above
  * `make`
* Have the following Python interpreters installed:
  * Python 2.7
  * Python 3.4
  * Python 3.5
* Have the following Python packages installed either to a virtualenv
  that you will run the test harness within, or to your host system etc.:
  * `tox`
  * `virtualenv`

### Caveats and Warnings

* Check for orphaned virtualbox instances from previous test runs using the Virtualbox admin tools.

### Usage

Please see the cheatsheet at the beginning of this doc for the general Make targets available.

## Running in the included Vagrant environment

### Prerequisites

Your host machine must have the following:

* A Unix-like operating system (Linux, Mac OS).
  * Windows is *not* supported.
* Have the following non-pythonic tools installed:
  * Vagrant version 1.8.5 or above
  * Virtualbox version 5.1 or above
* Have the following Python interpreters installed:
  * Python 2.7
* Have the following Python packages installed
  * `virtualenv`

### Caveats and Warnings

If you are running the test harness within the included Vagrant environment, then only tests that do
not themselves need to run Vagrant will work within the included Vagrant test host VM.

### Usage

A ``trusty`` sandbox VM is defined in the included Vagrantfile and you can hoist it up on
VirtualBox on your host as follows:

```
cd <repo>

# first setup ansible in a virtualenv
virtualenv .virtualenv
source .virtualenv/bin/activate
pip install -U pip==8.1.2
pip install -U ansible==2.2.0

# now run vagrant while the virtualenv is activated in order to use ansible provisioner
vagrant up
vagrant ssh -c "cd /home/vagrant/cleanroom/testing && make clean test_make"
```

Please see the cheatsheet at the beginning of this doc for the general Make targets available.

## Running On the Spetsnaz OpenStack Alpha Cluster

### Prerequisites

Your host machine must have the following:

* A Unix-like operating system (Linux, Mac OS).
  * Windows is *not* supported.
* Have the following non-pythonic tools installed:
  * Vagrant version 1.8.5 or above
  * Virtualbox version 5.1 or above
* Have the following Python interpreters installed:
  * Python 2.7
* Have the following Python packages installed
  * `virtualenv`

### Caveats and Warnings

At the time of this writing, OpenStack *could* support running VirtualBox
within an OpenStack curated VM, but the "alpha" cluster doesn't have that
configuration set yet. (for good reason, as it a rather odd edge case).

If the need becomes great enough, we can sync with Spetsnaz to look into
getting that enabled to some degree.

However, for now, only tests that do not themselves need to run Vagrant will
work within the included Vagrant test host VM.

### Usage

This repo includes a ``terraform`` config to allow you to stand up a dev/test sandbox
in our in-house "alpha" OpenStack cluster (managed by the Spetsnaz group).

Read [their quickstart guide first](https://pages.git.edgecastcdn.net/spetsnaz-docs/openstack-quickstart-guide/).

Several make targets have been added to smooth out your use of the included terraform recipes.

Below is an example that assumes you are managing your secrets in terraform ``tfvars``
file.  There are other techniques using "stock" terraform features, but those are up to
you.

```
# Set the terraform flag for log level to DEBUG (personal preference when debugging a new setup)
export TF_LOG=debug

# change directories to your local clone of your fork of this repository
cd <repo>/testing

# setup a copy of the example secrets in some directory of your own and edit it to add
# your secrets
cp -v terraform/example-secrets.tfvars ~/your-super-secret-dir/openstack-alpha-secrets.tfvars
nano ~/your-super-secret-dir/openstack-alpha-secrets.tfvars

# smoke test your secrets etc. via terraform plan
make YOUR_TERRAFORM_SECRETS_FILE=~/your-super-secret-dir/openstack-alpha-secrets.tfvars run_tf_plan_for_alpha_cluster_vm

# spin up the vm
make YOUR_TERRAFORM_SECRETS_FILE=~/your-super-secret-dir/openstack-alpha-secrets.tfvars run_tf_apply_for_alpha_cluster_vm

# run this make file to clean up tf files that might have your secrets in them
make clean_terraform

# check openstack etc. for the IP address of the vm you made

#
# provision the vm using the same ansible playbook as is used to provision the included Vagrant environment
#
# make sure you have the ssh private key available (~/.ssh/inhouse-openstack-dev-box in this example)
#

# provision the vm itself
make YOUR_PRIVATE_KEY_FILE=~/.ssh/inhouse-openstack-dev-box THE_TERRAFORM_VM_IP_ADDRESS=<ip-address-of-openstack-vm> provision_alpha_cluster_vm

# upload your "src" to it
make YOUR_PRIVATE_KEY_FILE=~/.ssh/inhouse-openstack-dev-box THE_TERRAFORM_VM_IP_ADDRESS=<ip-address-of-openstack-vm> upload_src_to_alpha_cluster_vm

# now use ssh to run the tests (or login and run a tmux session with the same commands, which would be wiser in general)
# note that the example below also assumes your .ssh/config is setup to know about the ip-address of the openstack vm etc.
ssh <ip-address-of-openstack-vm> "cd /home/ubuntu/cleanroom/src/testing && make clean_all test_make"

# download your test output from it (will end up as the <rep>/testing/output directory)
make YOUR_PRIVATE_KEY_FILE=~/.ssh/inhouse-openstack-dev-box THE_TERRAFORM_VM_IP_ADDRESS=<ip-address-of-openstack-vm> download_from_alpha_cluster_vm

```

>
> **Remember to clean up after yourself!  Do not keep these VMs laying about if you don't need them.**
>
