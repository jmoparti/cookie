/************************************************************

  Terraform configuration for hosting build and testing of
  this project in Spetsnaz OpenStack.

  Assumptions:
  - You are going to use the "alpha" cluster
  - You are using your own EC credentials
************************************************************/

/*
  User provided variables
*/

variable "flavor_name" {
  description = "The openstack 'flavor' for the VM stood up as the dev sandbox"
  type = "string"
  default = "m1.xlarge"
}

variable "hostname" {
  description = "The hostname of the VM stood up as the dev sandbox"
  type = "string"
  default = "cc-sysops-py-pkg-dev-sandbox"
}

variable "ssh_key_pair" {
  description = "Name of your Openstack ssh key pair"
  type = "string"
}

variable "tenant_name" {
  description = "For example: SI or SYSOPS"
  type = "string"
}

variable "user_name" {
  description = "Your ECDC account name"
  type = "string"
}

variable "user_password" {
  description = "Your ECDC account password"
  type = "string"
}


/*
  Provider config
*/

provider "openstack" {
  auth_url  = "https://openstack.xla.edgecastcdn.net:5001/v3"
  domain_name = "ECDC"
  password  = "${var.user_password}"
  tenant_name = "${var.tenant_name}"
  user_name  = "${var.user_name}"
}

/*
  Resources
*/

resource "openstack_compute_instance_v2" "dev_sandbox" {

  # Hardcoded availability zone
  availability_zone = "nova"

  # Pick the large with 4 CPUs by default
  flavor_name = "${var.flavor_name}"

  # Hardcode the image to our EC 1404 for now
  image_name = "Ubuntu-1404-EC"

  # Parameterize the ssh key pair
  key_pair = "${var.ssh_key_pair}"

  # Parameterize the server name
  name = "${var.hostname}"

  # Hardcode the network name
  network {
    name = "provider-2029"
  }

  # Use default security groups
  security_groups = ["default"]

}