# Input variables for the week 9 VM. The defaults are the values for NTNU
# OpenStack (TRD1) from the lab's part 0 slide; your own name goes in
# terraform.tfvars (gitignored) - see terraform.tfvars.example.

# No default: the course project is shared, so every name must be yours.
# Two security groups with the same name make the VM ambiguous to OpenStack.
variable "server_name" {
  description = "Name of the VM, its key pair and its security group: lab-server-<your NTNU username>"
  type        = string
}

variable "image_name" {
  description = "Image the VM boots from"
  type        = string
  default     = "Ubuntu Server 24.04 LTS (Noble Numbat)"
}

variable "flavor_name" {
  description = "Size of the VM"
  type        = string
  default     = "gx3.1c2r"
}

variable "network_name" {
  description = "The course project's public network - the VM gets a public IP from it directly"
  type        = string
  default     = "idata2502-exposed"
}

variable "ssh_public_key_path" {
  description = "Path to your PUBLIC SSH key (.pub) - Terraform uploads it as an OpenStack key pair; the private key stays with you"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}
