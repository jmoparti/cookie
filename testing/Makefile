#**************************************************
#
# Test harness
#
#**************************************************

# general make config
SHELL := /bin/bash

# find test code
TESTS_SRC_DIR = tests
TESTS_PYC_FILES := $(shell find $(TESTS_SRC_DIR) -name "*.pyc")
TESTS_PYCACHE_FILES := $(shell find $(TESTS_SRC_DIR) -name "__pycache__")

#
# Makefile target config
#

.PHONY: all clean clean_all dirs lint_self lint_hooks tests test_make test_make_via_cli test_make_via_api test_vagrant_env

default: all

#
# Default target
#

all: clean tests

#
# Cleaning
#

clean:
	-rm -rfv .cookiecutters .replays test.log output/* .cache prof/
	-rm -rfv $(TESTS_PYC_FILES) $(TESTS_PYCACHE_FILES)

clean_virtualenvs:
	-rm -rfv .virtualenv .virtualenv_ansible

clean_all: clean_virtualenvs clean_terraform clean

#
# Setup scaffolding
#

.virtualenv_ansible/bin/activate:
	virtualenv .virtualenv_ansible
	.virtualenv_ansible/bin/pip install ansible==2.2.0

.virtualenv/bin/activate:
	virtualenv .virtualenv
	.virtualenv/bin/pip install -r requirements.txt

virtualenvs: .virtualenv/bin/activate .virtualenv_ansible/bin/activate

dirs:
	mkdir -p .cookiecutters output output/ad-hoc .replays

#
# Linting
#

lint_self: .virtualenv/bin/activate
	.virtualenv/bin/pylint --errors-only tests

lint_hooks: .virtualenv/bin/activate
	.virtualenv/bin/pylint --errors-only ../hooks/post_gen_project.py ../hooks/pre_gen_project.py

#
# Tests
#

test_make_via_api: .virtualenv/bin/activate dirs lint_self lint_hooks
	scripts/test-make-via-api.sh

test_make_via_cli: .virtualenv/bin/activate dirs lint_self lint_hooks
	scripts/test-make-via-cli.sh

smoke_test_make_via_api: .virtualenv/bin/activate dirs lint_self lint_hooks
	scripts/smoke-test-make-via-api.sh

test_make: smoke_test_make_via_api
	scripts/test-make.sh

test_vagrant_build_vm: .virtualenv/bin/activate dirs lint_self lint_hooks
	scripts/test-vagrant-build-vm.sh

test_vagrant_sys_test_vm: .virtualenv/bin/activate dirs lint_self lint_hooks
	scripts/test-vagrant-sys-test-vm.sh

test_vagrant_env: test_vagrant_build_vm test_vagrant_sys_test_vm

test_travis_env: .virtualenv/bin/activate dirs lint_self lint_hooks
	scripts/test-travis.sh

#
# Rollup of all available tests
#

tests: test_make test_vagrant_env test_travis_env

#
# Run the cookiecutter ad-hoc without tests
#

run_cookiecutter_with_input: .virtualenv/bin/activate dirs
	cd .. && ./testing/.virtualenv/bin/cookiecutter --output-dir ./testing/output/ad-hoc/ .

run_cookiecutter_wout_input: .virtualenv/bin/activate dirs
	cd .. && ./testing/.virtualenv/bin/cookiecutter --no-input --output-dir ./testing/output/ad-hoc/ .

#
# Running terraform
#

THE_TERRAFORM_VM_HOSTNAME := $(USER)-sysops-cc-py-pkg
YOUR_TERRAFORM_SECRETS_FILE := "<MISSING>"

## standing up the vm (but not provisioning it)

run_tf_plan_for_alpha_cluster_vm:
	@echo "Running terraform to provision a vm in spetz alpha cluster openstack"
	terraform plan -var hostname=$(THE_TERRAFORM_VM_HOSTNAME) -var-file=$(YOUR_TERRAFORM_SECRETS_FILE) terraform/

run_tf_apply_for_alpha_cluster_vm:
	@echo "Running terraform to provision a vm in spetz alpha cluster openstack"
	terraform apply -var hostname=$(THE_TERRAFORM_VM_HOSTNAME) -var-file=$(YOUR_TERRAFORM_SECRETS_FILE) terraform/

clean_terraform:
	@echo "Removing leftover terraform data files that might have sensitive info"
	-rm -fv terraform.tfstate

## Running ansible against terraform

THE_TERRAFORM_VM_IP_ADDRESS := "MISSING"
YOUR_PRIVATE_KEY_FILE := "MISSING"

provision_alpha_cluster_vm: .virtualenv_ansible/bin/activate
	@echo "provision the vm in the alphastack cluster with the same ansible playbook as for the local Vagrant"
	source .virtualenv_ansible/bin/activate && ansible-playbook --private-key $(YOUR_PRIVATE_KEY_FILE) --u ubuntu --extra-vars "remote_user_name=ubuntu" -v -i '$(THE_TERRAFORM_VM_IP_ADDRESS),' ansible/provision-openstack-alpha-vm.yml

upload_src_to_alpha_cluster_vm: .virtualenv_ansible/bin/activate
	@echo "Upload the test src to the vm in the alpha cluster"
	source .virtualenv_ansible/bin/activate && ansible-playbook --private-key $(YOUR_PRIVATE_KEY_FILE) --u ubuntu --extra-vars "remote_user_name=ubuntu" -v -i '$(THE_TERRAFORM_VM_IP_ADDRESS),' ansible/upload-test-src.yml

download_from_alpha_cluster_vm: .virtualenv_ansible/bin/activate
	@echo "download test output from vm in the alpha cluster"
	-rm rfv output/
	source .virtualenv_ansible/bin/activate && ansible-playbook --private-key $(YOUR_PRIVATE_KEY_FILE) --u ubuntu --extra-vars "remote_user_name=ubuntu" -v -i '$(THE_TERRAFORM_VM_IP_ADDRESS),' ansible/download-test-output.yml


#
# Running Vagrant
#

vagrant_up_trusty_sandbox: .virtualenv_ansible/bin/activate
	source .virtualenv_ansible/bin/activate && vagrant up trusty_sandbox

vagrant_provision_trusty_sandbox: .virtualenv_ansible/bin/activate
	source .virtualenv_ansible/bin/activate && vagrant provision trusty_sandbox

vagrant_destroy_trusty_sandbox:
	vagrant destroy -f trusty_sandbox

upload_src_to_trusty_sandbox: .virtualenv_ansible/bin/activate
	@echo "Upload the test src to the trusty sandbox vm in the Vagrant environment"
	source .virtualenv_ansible/bin/activate && ansible-playbook --private-key .vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory -i .vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory -v ansible/upload-test-src.yml
