# Provider configuration for the week 9 VM on NTNU OpenStack (SkyHigh, TRD1).
#
# The provider block says WHERE to authenticate, never WITH WHAT: `cloud` is
# the entry name in clouds.yaml, which the provider looks for in this folder,
# then in ~/.config/openstack/. clouds.yaml holds the application credential
# secret and is gitignored.
#
# The OpenStack API answers only inside NTNU: plan, apply and destroy need the
# campus network or VPN. The VM itself does not - SSH and the app are public.

terraform {
  required_version = ">= 1.5.0"

  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 3.0"
    }
  }
}

provider "openstack" {
  cloud  = "openstack"
  region = "TRD1" # the course network lives here; Horizon may default to TRD2
}
