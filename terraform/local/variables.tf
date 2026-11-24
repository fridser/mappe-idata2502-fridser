variable "ssh_public_key_path" {
  description = "Path to your PUBLIC SSH key (.pub) - Terraform copies its content onto the server; the private key stays with you"
  type        = string
  default     = "~/.ssh/id_ed25519.pub"
}

variable "ssh_port" {
  description = "Port on your machine that forwards to the server's SSH (22)"
  type        = number
  default     = 2222
}

variable "server_name" {
  description = "Name (and hostname) of the container that plays the server"
  type        = string
  default     = "mappe-server"
}
