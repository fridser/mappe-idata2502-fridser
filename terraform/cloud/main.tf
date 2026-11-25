resource "openstack_compute_keypair_v2" "key" {
   name       = "${var.server_name}-key"
   public_key = file(pathexpand(var.ssh_public_key_path))
}

resource "openstack_networking_secgroup_v2" "server" {
    name = "${var.server_name}-sg" # the name you see in Horizon
}

resource "openstack_networking_secgroup_rule_v2" "ssh" {
    direction = "ingress" # traffic IN to the VM
    ethertype = "IPv4"
    protocol = "tcp"
    port_range_min = 22 # one port: min = max
    port_range_max = 22
    remote_ip_prefix = "0.0.0.0/0" # from anywhere - GitHub is not on campus
    security_group_id = openstack_networking_secgroup_v2.server.id # rule → group, by id
}

resource "openstack_networking_secgroup_rule_v2" "app" {
  direction         = "ingress"
  ethertype         = "IPv4"
  protocol          = "tcp"
  port_range_min    = 5000
  port_range_max    = 5000
  remote_ip_prefix  = "0.0.0.0/0"
  security_group_id = openstack_networking_secgroup_v2.server.id
}

resource "openstack_compute_instance_v2" "server" {
   name = var.server_name
   image_name  = var.image_name
   flavor_name = var.flavor_name
   key_pair = openstack_compute_keypair_v2.key.name
   security_groups = [openstack_networking_secgroup_v2.server.name]
   network { name = var.network_name }
}
