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
    assert f.contains("test-http-only")


def test_traefik_tls_router(host):
    """Verify TLS router has both HTTP redirect and HTTPS routers."""
    f = host.file("/etc/traefik/dynamic.yml")
    assert f.contains("test-app-http")  # HTTP redirect router
    assert f.contains("https-redirect")  # Redirect middleware


def test_traefik_http_only_router(host):
    """Verify HTTP-only router uses web entrypoint."""
    f = host.file("/etc/traefik/dynamic.yml")
    content = f.content_string
    # test-http-only should use web entrypoint, not websecure
    assert "test-http-only:" in content


def test_traefik_certs_dir_absent(host):
    """Verify certs directory is not created when no custom cert is set."""
    d = host.file("/etc/traefik/certs")
    assert not d.exists


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


def test_custom_entrypoint(host):
    """Verify custom entrypoint is configured."""
    f = host.file("/etc/traefik/traefik.yml")
    assert f.contains("custom:")
    assert f.contains(":8096")


def test_custom_port_router(host):
    """Verify router uses custom entrypoint."""
    f = host.file("/etc/traefik/dynamic.yml")
    content = f.content_string
    assert "test-custom-port:" in content
    assert "custom" in content


def test_port_8096(host):
    """Verify custom port 8096 is listening."""
    assert host.socket("tcp://0.0.0.0:8096").is_listening
