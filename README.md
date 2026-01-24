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
    urls:
      - "http://192.168.1.10:8080"
  - name: api
    urls:
      - "http://192.168.1.11:3000"
      - "http://192.168.1.12:3000"
```

### TCP Entrypoints

Define custom TCP entrypoints using `traefik_tcp_entrypoints`:

```yaml
traefik_tcp_entrypoints:
  - name: mydb
    port: 5432
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
| 80 | HTTP (redirects to HTTPS) |
| 443 | HTTPS |
| Custom | TCP entrypoints (defined via `traefik_tcp_entrypoints`) |

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
