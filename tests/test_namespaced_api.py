# tests/test_namespaced_api.py
import time
import pytest

try:
    from parolo import prompts
except Exception:
    pytest.skip("prompts namespace not available", allow_module_level=True)

pytest.importorskip("jinja2")

def test_prompts_save_read_render(tmp_path, monkeypatch):
    monkeypatch.setenv("PAROLO_HOME", str(tmp_path))
    prompts.set_base_dir(tmp_path)   # ← ensure BASE_DIR = tmp_path

    prompts.save("greet", "Hello {{ name }}!")
    assert prompts.read("greet") == "Hello {{ name }}!"
    assert prompts.versions("greet") == ["v0001.txt"]
    assert prompts.render("greet", name="Matthias") == "Hello Matthias!"

def test_prompts_list_and_meta(tmp_path, monkeypatch):
    monkeypatch.setenv("PAROLO_HOME", str(tmp_path))
    prompts.set_base_dir(tmp_path)   # ← add here too

    prompts.save("a", "A")
    prompts.save("b", "B1")
    prompts.save("b", "B2")

    all_prompts = prompts.list()
    names = {p["name"] for p in all_prompts}
    assert {"a", "b"} <= names

    vers = prompts.versions("b", with_meta=True)
    assert len(vers) == 2
    assert "timestamp" in vers[-1]
    assert "hash" in vers[-1]
