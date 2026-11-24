
resource "docker_image" "server" {
  name = "mappe-server:latest"
    build {
    context = "${path.module}/server"
   }
  triggers = {
   dockerfile = filesha256("${path.module}/server/Dockerfile")
   }
}

resource "docker_network" "lab" {
  name = "mappe-server"
}

 resource "docker_container" "server" {
   name     = var.server_name
  hostname = var.server_name
  image    = docker_image.server.image_id
  restart  = "unless-stopped"

  privileged = true
 

 ports {
    internal = 22
    external = var.ssh_port
  }

 networks_advanced { 
    name = docker_network.lab.name 
    }

   volumes {
    container_path = "/var/lib/docker"
  }

  volumes {
    container_path = "/var/lib/containerd"
  }

upload {
   file    = "/home/ubuntu/.ssh/authorized_keys"
    content = file(pathexpand(var.ssh_public_key_path))
}
}