"""Tests for ansible-role-traefik."""


def test_traefik_config_dir(host):
    """Verify traefik config directory exists."""
    d = host.file("/etc/traefik")
    assert d.exists
    assert d.is_directory


def test_traefik_static_config(host):
    """Verify static configuration file exists and contains expected content."""
    f = host.file("/etc/traefik/traefik.yml")
    assert f.exists
    assert f.is_file
    assert f.contains("entryPoints")
    assert f.contains("websecure")


def test_traefik_docker_provider(host):
    """Verify Docker provider is enabled in static config."""
    f = host.file("/etc/traefik/traefik.yml")
    assert f.contains("docker")
    assert f.contains("exposedByDefault: false")


def test_traefik_http_to_https_redirect(host):
    """Verify HTTP to HTTPS redirection is configured."""
    f = host.file("/etc/traefik/traefik.yml")
    assert f.contains("redirections")
    assert f.contains("websecure")


def test_traefik_acme_absent(host):
    """Verify ACME is not configured when email is not set."""
    f = host.file("/etc/traefik/traefik.yml")
    assert not f.contains("certificatesResolvers")
    d = host.file("/etc/traefik/acme")
    assert not d.exists


def test_traefik_container_running(host):
    """Verify traefik container is running."""
    cmd = host.run("docker ps --filter name=traefik --format '{{.Status}}'")
    assert "Up" in cmd.stdout


def test_docker_socket_mounted(host):
    """Verify Docker socket is mounted in the container."""
    cmd = host.run("docker inspect traefik --format '{{.HostConfig.Binds}}'")
    assert "/var/run/docker.sock" in cmd.stdout


def test_port_80(host):
    """Verify port 80 is listening."""
    assert host.socket("tcp://0.0.0.0:80").is_listening


def test_port_443(host):
    """Verify port 443 is listening."""
    assert host.socket("tcp://0.0.0.0:443").is_listening
