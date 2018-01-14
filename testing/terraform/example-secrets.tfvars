#
# This is an example of a tfvars file you could use with
# terraform commands to store "secrets", e.g. run commands like `terraform --var-file ~/super-secret.tfvars plan`
#
# There are many other approaches as well.
# No matter what, DO NOT CHECK YOUR ECDC PASSWORD INTO THIS REPOSITORY
# This is AN EXAMPLE FILE ONLY, DO NOT CHECK IN YOUR REAL SECRETS / SETTINGS TO THIS REPOSITORY!!!
#

ssh_key_pair = "<Name of the openstack key pair you want to use>"
tenant_name = "<Put your tenent name here, e.g. SI, SYSOPS, or somesuch"
user_name ="<Your ECDC user name>"
user_password = "<Your ECDC uer password>"
