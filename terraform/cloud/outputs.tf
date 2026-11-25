# Where the VM is. Week 9 puts public_ip into ansible/inventory.ini and the
# VM_HOST secret.
#
# Finished, but commented out: the outputs refer to the VM from block 3, and
# until that block exists every `terraform plan` would fail with "Reference to
# undeclared resource". When block 3 is written, remove the leading "# " from
# the output blocks below - NOT from this comment (select from `# output` to
# the end, then your editor's toggle-comment shortcut) - and plan again.

output "public_ip" {
    value = openstack_compute_instance_v2.server.access_ip_v4
}

output "ssh_command" {
    value = "ssh ubuntu@${openstack_compute_instance_v2.server.access_ip_v4}"
}

output "app_url" {
    value = "http://${openstack_compute_instance_v2.server.access_ip_v4}:5000"
}
