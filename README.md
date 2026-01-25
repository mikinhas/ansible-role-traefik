# Ansible Role: Traefik

An Ansible role to deploy [Traefik](https://traefik.io/) reverse proxy as a Docker container with automatic HTTPS via Let's Encrypt.

## Features

- Traefik v3.2 deployed as a Docker container
- Automatic HTTP to HTTPS redirection
- Let's Encrypt certificate management (ACME)
- Dynamic configuration for HTTP and TCP routers and services
- Security headers middleware (HSTS, XSS protection, etc.)
- TLS 1.2+ with strong cipher suites

## Requirements

- Ansible >= 2.16
- `community.docker` collection
- `community.general` collection

Install dependencies:

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

### ACME / Let's Encrypt (optional)

| Variable               | Default                                          | Description                                                      |
|------------------------|--------------------------------------------------|------------------------------------------------------------------|
| `traefik_acme_email`   | `""`                                             | Email for Let's Encrypt registration. If empty, ACME is disabled |
| `traefik_acme_server`  | `https://acme-v02.api.letsencrypt.org/directory` | ACME server URL                                                  |

> **Note**: When `traefik_acme_email` is not set, the ACME directory and certificate resolver are not created. Traefik will run without automatic certificate management.

### Custom TLS Certificates (optional)

Use your own certificates instead of ACME:

| Variable | Default | Description |
|----------|---------|-------------|
| `traefik_tls_cert` | `""` | Path to the certificate file (PEM format) |
| `traefik_tls_key` | `""` | Path to the private key file (PEM format) |

```yaml
traefik_tls_cert: "/path/to/wildcard.pem"
traefik_tls_key: "/path/to/wildcard-key.pem"
```

> **Note**: Custom certificates take precedence over ACME. When both `traefik_tls_cert` and `traefik_tls_key` are set, the certificate files are copied to the target host and used for all `tls: true` routers.

### HTTP Routers

Define your HTTP routers using `traefik_http_routers`:

```yaml
traefik_http_routers:
  # HTTPS with automatic HTTP to HTTPS redirect
  - name: myapp
    rule: "Host(`myapp.example.com`)"
    service: myapp
    tls: true

  # HTTP only (no redirect, no TLS)
  - name: internal-api
    rule: "Host(`api.internal.local`)"
    service: internal-api
    tls: false
```

| Option | Description |
|--------|-------------|
| `tls: true` | HTTPS on port 443 + automatic HTTP→HTTPS redirect on port 80 |
| `tls: false` | HTTP only on port 80 (no redirect, no TLS) |

### Services

Define backend services using `traefik_services`:

```yaml
traefik_services:
  - name: myapp
    urls:
      - "http://192.168.1.10:8080"
  - name: api
    urls:
      - "http://192.168.1.11:3000"
      - "http://192.168.1.12:3000"
```

### Custom Entrypoints

Define custom entrypoints for services that need dedicated ports:

```yaml
traefik_entrypoints:
  - name: custom
    port: 8080
  - name: mydb
    port: 5432
```

Then reference the entrypoint in your router:

```yaml
traefik_http_routers:
  - name: myapp
    rule: "PathPrefix(`/`)"
    service: myapp
    tls: false
    entrypoint: custom
```

### TCP Routers

Define TCP routers using `traefik_tcp_routers`:

```yaml
traefik_tcp_routers:
  - name: mydb
    entrypoint: mydb
    rule: "HostSNI(`*`)"
    service: mydb
```

### TCP Services

Define TCP backend services using `traefik_tcp_services`:

```yaml
traefik_tcp_services:
  - name: mydb
    urls:
      - "192.168.1.10:5432"
      - "192.168.1.11:5432"
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
            urls:
              - "http://10.0.0.5:8080"
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
| 80 | HTTP (redirects to HTTPS when `tls: true`, or serves directly when `tls: false`) |
| 443 | HTTPS |
| Custom | Custom entrypoints (defined via `traefik_entrypoints`) |

## Testing

This role uses [Molecule](https://molecule.readthedocs.io/) with Vagrant and VirtualBox for testing.

```bash
pip install -r requirements.txt
molecule test
```

The default scenario tests the role on Ubuntu Noble (24.04) without ACME enabled.

## License

MIT

## Author

Michael MACHADO
