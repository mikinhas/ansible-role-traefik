# Ansible Role: Traefik

An Ansible role to deploy [Traefik](https://traefik.io/) reverse proxy as a Docker container with automatic HTTPS via Let's Encrypt.

## Features

- Traefik v3.2 deployed as a Docker container
- Automatic HTTP to HTTPS redirection
- Let's Encrypt certificate management (ACME)
- Dynamic configuration for HTTP routers and services
- Security headers middleware (HSTS, XSS protection, etc.)
- TLS 1.2+ with strong cipher suites

## Requirements

- Ansible >= 2.16
- Docker installed on the target host
- `community.docker` collection

## Dependencies

- `mikinhas.docker` - Installs and configures Docker

## Role Variables

### Basic Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `traefik_version` | `v3.2` | Traefik Docker image version |
| `traefik_container_name` | `traefik` | Name of the Docker container |
| `traefik_config_dir` | `/etc/traefik` | Configuration directory on the host |

### ACME / Let's Encrypt (optional)

| Variable               | Default                                          | Description                                                      |
|------------------------|--------------------------------------------------|------------------------------------------------------------------|
| `traefik_acme_email`   | `""`                                             | Email for Let's Encrypt registration. If empty, ACME is disabled |
| `traefik_acme_server`  | `https://acme-v02.api.letsencrypt.org/directory` | ACME server URL                                                  |

> **Note**: When `traefik_acme_email` is not set, the ACME directory and certificate resolver are not created. Traefik will run without automatic certificate management.

### HTTP Routers

Define your HTTP routers using `traefik_http_routers`:

```yaml
traefik_http_routers:
  - name: myapp
    rule: "Host(`myapp.example.com`)"
    service: myapp
    tls: true
  - name: api
    rule: "Host(`api.example.com`) && PathPrefix(`/v1`)"
    service: api
    tls: true
```

### Services

Define backend services using `traefik_services`:

```yaml
traefik_services:
  - name: myapp
    url: "http://192.168.1.10:8080"
  - name: api
    url: "http://192.168.1.11:3000"
```

## Example Playbook

```yaml
- hosts: reverse_proxy
  roles:
    - role: mikinhas.traefik
      vars:
        traefik_acme_email: "admin@example.com"
        traefik_http_routers:
          - name: webapp
            rule: "Host(`app.example.com`)"
            service: webapp
            tls: true
        traefik_services:
          - name: webapp
            url: "http://10.0.0.5:8080"
```

## Security Features

This role configures Traefik with security best practices:

- **HSTS**: Strict Transport Security enabled with preload
- **Content-Type sniffing**: Disabled
- **XSS Filter**: Enabled
- **Frame options**: Deny (clickjacking protection)
- **Referrer Policy**: strict-origin-when-cross-origin
- **TLS**: Minimum version TLS 1.2 with strong cipher suites

## Exposed Ports

| Port | Description |
|------|-------------|
| 80 | HTTP (redirects to HTTPS) |
| 443 | HTTPS |

## License

MIT

## Author

Michael MACHADO
