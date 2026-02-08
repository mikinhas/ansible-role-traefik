# Ansible Role: Traefik

An Ansible role to deploy [Traefik](https://traefik.io/) reverse proxy as a Docker container.

## Features

- Traefik v3.2 deployed as a Docker container
- Automatic HTTP to HTTPS redirection
- Let's Encrypt certificate management (ACME)
- Custom TLS certificates (wildcard support)
- HTTP and TCP routing with load balancing
- Security headers middleware (HSTS, XSS protection, etc.)
- TLS 1.2+ with strong cipher suites

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
| `traefik_version` | `v3.2` | Traefik Docker image version |
| `traefik_container_name` | `traefik` | Name of the Docker container |
| `traefik_config_dir` | `/etc/traefik` | Configuration directory on the host |
| `traefik_networks` | `[]` | Docker networks to attach |

### ACME / Let's Encrypt

| Variable | Default | Description |
|----------|---------|-------------|
| `traefik_acme_email` | `""` | Email for Let's Encrypt. If empty, ACME is disabled |
| `traefik_acme_server` | `https://acme-v02.api.letsencrypt.org/directory` | ACME server URL |

### Custom TLS Certificates

| Variable | Default | Description |
|----------|---------|-------------|
| `traefik_tls_cert` | `""` | Path to the certificate file (PEM) |
| `traefik_tls_key` | `""` | Path to the private key file (PEM) |

## HTTP Routes

Define HTTP routes using `traefik_http`:

```yaml
traefik_http:
  # HTTPS route (ports 80 redirect + 443)
  - name: myapp
    rule: Host(`myapp.example.com`)
    tls: true
    backends:
      - http://192.168.1.10:8080
      - http://192.168.1.11:8080

  # HTTPS with self-signed backend
  - name: api
    rule: Host(`api.example.com`)
    tls: true
    backends:
      - https://192.168.1.20:443
    skip_tls_verify: true

  # HTTP on custom port with Host header rewrite
  - name: jellyfin
    rule: PathPrefix(`/`)
    port: 8096
    backends:
      - https://192.168.1.20:443
    skip_tls_verify: true
    host_header: jellyfin.example.com

  # HTTPS with IP allowlist
  - name: prometheus
    rule: Host(`prometheus.example.com`)
    tls: true
    backends:
      - http://192.168.1.30:9090
    allowed_ips:
      - 82.100.0.1/32
      - 192.168.1.0/24
```

### HTTP Route Options

| Option | Required | Description |
|--------|----------|-------------|
| `name` | yes | Unique route name |
| `rule` | yes | Traefik routing rule |
| `backends` | yes | List of backend URLs |
| `tls` | no | Enable HTTPS + HTTP redirect (default: false) |
| `port` | no | Custom port (creates entrypoint automatically) |
| `skip_tls_verify` | no | Skip TLS verification for HTTPS backends |
| `host_header` | no | Override Host header sent to backend |
| `allowed_ips` | no | List of CIDR ranges allowed to access the route |

## TCP Routes

Define TCP routes using `traefik_tcp`:

```yaml
traefik_tcp:
  # TCP with TLS passthrough (for K8s API, databases, etc.)
  - name: k8s-api
    port: 6443
    rule: HostSNI(`*`)
    tls_passthrough: true
    backends:
      - 192.168.1.100:6443
      - 192.168.1.101:6443

  # Simple TCP proxy
  - name: postgres
    port: 5432
    rule: HostSNI(`*`)
    backends:
      - 192.168.1.50:5432
```

### TCP Route Options

| Option | Required | Description |
|--------|----------|-------------|
| `name` | yes | Unique route name |
| `port` | yes | TCP port (creates entrypoint automatically) |
| `rule` | yes | Traefik routing rule (usually `HostSNI(\`*\`)`) |
| `backends` | yes | List of backend addresses (host:port) |
| `tls_passthrough` | no | Pass TLS through without terminating |

## Example Playbook

```yaml
- hosts: reverse_proxy
  roles:
    - role: mikinhas.traefik
      vars:
        traefik_tls_cert: "files/wildcard.pem"
        traefik_tls_key: "files/wildcard-key.pem"

        traefik_networks:
          - name: mynetwork

        traefik_http:
          - name: webapp
            rule: Host(`app.example.com`)
            tls: true
            backends:
              - http://10.0.0.5:8080

        traefik_tcp:
          - name: k8s-api
            port: 6443
            rule: HostSNI(`*`)
            tls_passthrough: true
            backends:
              - 192.168.1.100:6443
```

## Security Features

- **HSTS**: Strict Transport Security with preload
- **Content-Type sniffing**: Disabled
- **XSS Filter**: Enabled
- **Frame options**: Deny (clickjacking protection)
- **Referrer Policy**: strict-origin-when-cross-origin
- **TLS**: Minimum TLS 1.2 with strong cipher suites

## Exposed Ports

| Port | Description |
|------|-------------|
| 80 | HTTP (redirects to HTTPS when `tls: true`) |
| 443 | HTTPS |
| Custom | TCP/HTTP custom ports (defined via `port` in routes) |

## Testing

```bash
pip install -r requirements.txt
molecule test
```

## License

MIT

## Author

Michael MACHADO
