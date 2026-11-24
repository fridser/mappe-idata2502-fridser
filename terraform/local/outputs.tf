output "ssh_command" {
  value = "ssh -p ${var.ssh_port} ubuntu@localhost"
}
