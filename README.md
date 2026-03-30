# Ansible Role: Traefik

An Ansible role to deploy [Traefik](https://traefik.io/) reverse proxy as a Docker container.

## Features

- Traefik v3.6 deployed as a Docker container
- Automatic HTTP to HTTPS redirection (enabled by default)
- Let's Encrypt certificate management (ACME)
- Docker provider support (auto-discovery via container labels)
- Custom environment variables and Docker networks

## Requirements

- Ansible >= 2.16
- `community.docker` collection
- `community.general` collection

```bash
ansible-galaxy install -r requirements.yml
```

## Dependencies

- `mikinhas.docker` - Installs and configures Docker

## Role Variables

### Basic Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `traefik_version` | `v3.6` | Traefik Docker image version |
| `traefik_container_name` | `traefik` | Name of the Docker container |
| `traefik_config_dir` | `/etc/traefik` | Configuration directory on the host |
| `traefik_docker_provider` | `false` | Enable Docker provider for auto-discovery |
| `traefik_http_to_https` | `true` | Redirect HTTP to HTTPS |
| `traefik_env` | `{}` | Environment variables passed to the container |
| `traefik_networks` | `[]` | Docker networks to attach |

### ACME / Let's Encrypt

| Variable | Default | Description |
|----------|---------|-------------|
| `traefik_acme_email` | `""` | Email for Let's Encrypt. If empty, ACME is disabled |
| `traefik_acme_server` | `https://acme-v02.api.letsencrypt.org/directory` | ACME server URL |

## Example Playbook

### Minimal (static reverse proxy)

```yaml
- hosts: reverse_proxy
  roles:
    - role: mikinhas.traefik
```

### With Docker provider and Let's Encrypt

```yaml
- hosts: reverse_proxy
  roles:
    - role: mikinhas.traefik
      vars:
        traefik_docker_provider: true
        traefik_acme_email: admin@example.com
        traefik_networks:
          - name: web
```

Then use Docker labels on your containers to configure routing:

```yaml
services:
  myapp:
    image: myapp:latest
    labels:
      traefik.enable: "true"
      traefik.http.routers.myapp.rule: Host(`myapp.example.com`)
      traefik.http.routers.myapp.entrypoints: websecure
      traefik.http.routers.myapp.tls.certresolver: letsencrypt
      traefik.http.services.myapp.loadbalancer.server.port: "8080"
    networks:
      - web
```

### With custom environment variables

```yaml
- hosts: reverse_proxy
  roles:
    - role: mikinhas.traefik
      vars:
        traefik_env:
          CF_DNS_API_TOKEN: "my-cloudflare-token"
```

## Exposed Ports

| Port | Description |
|------|-------------|
| 80 | HTTP (redirects to HTTPS by default) |
| 443 | HTTPS |

## Testing

```bash
pip install -r requirements.txt
molecule test
```

## License

MIT

## Author

Michael MACHADO
