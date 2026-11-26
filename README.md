# Final project

**Frida's project repository** for the final project in IDATA2502 Administration of Cloud Services.

The project takes a small Flask webapp (the "life shop", where you can buy love, happiness and success) and runs it through a full delivery loop: tests, a container image, a security scan, a registry, infrastructure as code, configuration management, automatic deployment to a VM on NTNU OpenStack, and an observability stack covering metrics, logs and traces.

## The delivery loop

```
push to a branch ──► CI: unit tests ─► build image ─► smoke test ─► Trivy scan
                     + dependency review (branches and PRs)
                                │
merge to main ──────────────────┴──► publish image to ghcr.io (:latest and :<sha>)
                                          │
                                          ▼
                               deploy: SSH to the VM, docker compose pull && up -d
```

1. **Terraform** ([terraform/cloud/](terraform/cloud/)) creates the VM, its SSH key pair and a security group that opens ports 22 (SSH) and 5000 (the app).
2. **Ansible** ([ansible/site.yml](ansible/site.yml)) installs Docker and Docker Compose, adds a 2 GB swapfile, and copies the deploy compose file and the monitoring config onto the VM.
3. **GitHub Actions** ([.github/workflows/ci.yml](.github/workflows/ci.yml)) tests, builds, scans and publishes the image, then deploys it to the VM over SSH. All actions are pinned to a commit SHA.

## Structure

```
.
|-- .github/
|   |-- workflows/ci.yml   # CI/CD pipeline: test, build, scan, publish, deploy
|   `-- dependabot.yml     # Automatic dependency update PRs
|-- app/                   # The Flask app, its tests and Dockerfile (see app/README.md)
|-- terraform/
|   |-- cloud/             # The production VM on NTNU OpenStack (SkyHigh, TRD1)
|   `-- local/             # A Docker container that acts as a server, for local testing
|-- ansible/site.yml       # Configures the server: Docker, swap, compose file, stack config
|-- deploy/compose.yaml    # The compose file Ansible puts on the VM
|-- compose.yaml           # The same stack, for running locally
|-- prometheus/            # Metrics: scrapes the app's /metrics endpoint
|-- alloy/                 # Logs: reads every container's stdout and ships it to Loki
|-- tempo/                 # Traces: receives OpenTelemetry spans from the app
|-- grafana/               # Data sources and five dashboards, provisioned as code
`-- .gitignore             # Keeps secrets, state files and .env out of git
```

## The stack

| Service    | Purpose                                                | Port  |
| ---------- | ------------------------------------------------------ | ----- |
| app        | The Flask app, instrumented with OpenTelemetry         | 5000  |
| redis      | Stores the visit and purchase counters (on a volume)   | -     |
| prometheus | Metrics, scraped from the app every 5 seconds          | 9090  |
| loki       | Log storage                                            | -     |
| alloy      | Log collector, finds containers via the Docker socket  | 12345 |
| tempo      | Trace storage, also writes service-graph metrics       | -     |
| grafana    | One UI for metrics, logs and traces                    | 3000  |

Every container has a memory limit, so the stack fits on a 2 GB VM.

Grafana comes with five dashboards: `up` (the home dashboard), `shop`, `metrics`, `logs` and `traces`.

## Run it locally

Requires Docker with Compose.

```bash
export GRAFANA_ADMIN_PASSWORD=<choose a password>
docker compose up -d
```

- App: <http://localhost:5000>
- Grafana: <http://localhost:3000> (user `admin`)
- Prometheus: <http://localhost:9090>

To run only the app without Docker, see [app/README.md](app/README.md).

### Test the Ansible playbook against a local server

[terraform/local/](terraform/local/) starts an Ubuntu container with systemd and SSH that acts as a server, so the playbook can be tested without a cloud VM:

```bash
cd terraform/local
terraform init
terraform apply
# SSH: ssh -p 2222 ubuntu@localhost
```

## Deploy to the cloud

The OpenStack API only answers inside NTNU, so Terraform needs the campus network or VPN.

1. **Create the VM.** Put a `clouds.yaml` with an application credential in [terraform/cloud/](terraform/cloud/) or `~/.config/openstack/`, and set `server_name` in `terraform.tfvars`. Both files are gitignored.

   ```bash
   cd terraform/cloud
   terraform init
   terraform apply
   ```

   The outputs give the public IP, the SSH command and the app URL.

2. **Configure the VM.** Create `ansible/inventory.ini` (gitignored) with the VM's IP under the group `[app]`, then run:

   ```bash
   cd ansible
   ansible-playbook -i inventory.ini site.yml
   ```

3. **Set the repository secrets** in GitHub:

   | Secret                   | Value                                     |
   | ------------------------ | ----------------------------------------- |
   | `VM_HOST`                | The VM's public IP                        |
   | `SSH_KEY`                | The private SSH key for the `ubuntu` user |
   | `GRAFANA_ADMIN_PASSWORD` | The Grafana admin password                |

4. **Merge to `main`.** The pipeline publishes a new image and deploys it to the VM.

Only ports 22 and 5000 are open on the VM. To reach Grafana, use an SSH tunnel:

```bash
ssh -L 3000:localhost:3000 ubuntu@<VM IP>
```

Then open <http://localhost:3000>.

## Security

- Secrets (Grafana password, SSH key, VM address) live in GitHub secrets, never in the repo.
- The app image runs as a non-root system user, removes `pip`, and pulls in Debian security updates at build time.
- Trivy fails the build on fixable critical and high vulnerabilities.
- Dependency review checks new dependencies on pull requests, and Dependabot opens update PRs.
- All GitHub Actions are pinned to a full commit SHA.
