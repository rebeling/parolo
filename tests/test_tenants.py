# tests/test_tenants.py
import time
import pytest

# Skip cleanly if tenants or prompts namespace isn't available yet
try:
    from parolo import tenants, prompts
except Exception:
    pytest.skip("parolo.tenants / parolo.prompts not available", allow_module_level=True)


def setup_tmp(parolo_home, tmp_path):
    # ensure both namespaces point at the per-test directory
    parolo_home.setenv("PAROLO_HOME", str(tmp_path))
    prompts.set_base_dir(tmp_path)


def test_key_format():
    assert tenants.key("acme", "support") == "acme_support"


def test_save_and_read_latest_semver(tmp_path, monkeypatch):
    setup_tmp(monkeypatch, tmp_path)

    # Save explicit 1.0.0
    info1 = tenants.save("t1", "a1", "V1", semver="1.0.0")
    assert info1["semver"] == "1.0.0"

    # Save without semver → auto 1.0.1
    info2 = tenants.save("t1", "a1", "V2")
    assert info2["semver"] == "1.0.1"

    # Latest semver is the last one
    assert tenants.latest_semver("t1", "a1") == "1.0.1"

    # Read by semver
    assert tenants.read("t1", "a1", semver="1.0.0") == "V1"
    # Read latest
    assert tenants.read("t1", "a1") == "V2"

    # Check metadata contains semver
    vers = prompts.versions("t1_a1", with_meta=True)
    latest_v = vers[-1]["version"]
    meta = prompts.meta("t1_a1", latest_v)
    assert meta.get("metadata", {}).get("semver") == "1.0.1"


def test_list_semvers_order_and_auto_increment(tmp_path, monkeypatch):
    setup_tmp(monkeypatch, tmp_path)

    tenants.save("org", "bot", "first", semver="1.0.0")
    tenants.save("org", "bot", "second", semver="1.0.1")
    # auto → should become 1.0.2
    tenants.save("org", "bot", "third")

    semvers = tenants.list_semvers("org", "bot")
    assert semvers == ["1.0.0", "1.0.1", "1.0.2"]


def test_ensure_initial_and_no_overwrite(tmp_path, monkeypatch):
    setup_tmp(monkeypatch, tmp_path)

    # First call creates initial
    created = tenants.ensure_initial("t2", "x", "initial", semver="1.0.0")
    assert created == "1.0.0"
    assert tenants.read("t2", "x") == "initial"

    # Second call does nothing by default
    again = tenants.ensure_initial("t2", "x", "should-not-overwrite", semver="1.0.0")
    assert again is None
    assert tenants.read("t2", "x") == "initial"

    # Overwrite = True forces a new save (same semver allowed by metadata)
    forced = tenants.ensure_initial("t2", "x", "overwritten", semver="1.0.0", overwrite=True)
    assert forced == "1.0.0"
    assert tenants.read("t2", "x") == "overwritten"


def test_read_with_fallback(tmp_path, monkeypatch):
    setup_tmp(monkeypatch, tmp_path)

    # No prompt exists; fallback supplies content
    fb = lambda: "fallback-text"
    assert tenants.read("no", "such", fallback=fb) == "fallback-text"

    # If fallback returns None, should raise
    with pytest.raises(Exception):
        tenants.read("no", "such", fallback=lambda: None)


def test_read_cached_updates_on_change(tmp_path, monkeypatch):
    setup_tmp(monkeypatch, tmp_path)

    tenants.save("t3", "a", "one", semver="1.0.0")
    v1 = tenants.read_cached("t3", "a")
    assert v1 == "one"

    # Ensure mtime tick on some filesystems
    time.sleep(0.01)

    tenants.save("t3", "a", "two", semver="1.0.1")
    v2 = tenants.read_cached("t3", "a")
    assert v2 == "two"
