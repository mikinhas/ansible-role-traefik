"""Tests for ansible-role-traefik."""


def test_traefik_config_dir(host):
    """Verify traefik config directory exists."""
    d = host.file("/etc/traefik")
    assert d.exists
    assert d.is_directory


def test_traefik_acme_dir_absent(host):
    """Verify ACME directory is not created when acme_email is not set."""
    d = host.file("/etc/traefik/acme")
    assert not d.exists


def test_traefik_static_config(host):
    """Verify static configuration file exists and contains expected content."""
    f = host.file("/etc/traefik/traefik.yml")
    assert f.exists
    assert f.is_file
    assert f.contains("entryPoints")
    assert not f.contains("certificatesResolvers")


def test_traefik_dynamic_config(host):
    """Verify dynamic configuration file exists and contains expected content."""
    f = host.file("/etc/traefik/dynamic.yml")
    assert f.exists
    assert f.is_file
    assert f.contains("test-app")


def test_traefik_container_running(host):
    """Verify traefik container is running."""
    cmd = host.run("docker ps --filter name=traefik --format '{{.Status}}'")
    assert "Up" in cmd.stdout


def test_port_80(host):
    """Verify port 80 is listening."""
    assert host.socket("tcp://0.0.0.0:80").is_listening


def test_port_443(host):
    """Verify port 443 is listening."""
    assert host.socket("tcp://0.0.0.0:443").is_listening
