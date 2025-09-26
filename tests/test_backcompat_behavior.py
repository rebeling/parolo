import time
from parolo import Prompt

def test_latest_mtime_changes(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    Prompt.create("mtime", "v1")
    latest = Prompt.base_dir / "mtime" / "latest.txt"
    t1 = latest.stat().st_mtime_ns

    time.sleep(0.01)
    Prompt.create("mtime", "v2")
    t2 = latest.stat().st_mtime_ns
    assert t2 != t1  # confirms atomic replace and detectable change

def test_get_prompt_specific_with_txt_suffix(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")
    Prompt.create("suffix", "S1")
    Prompt.create("suffix", "S2")

    assert Prompt.get_prompt("suffix", "v0001.txt") == "S1"
    assert Prompt.get_prompt("suffix", "v0002.txt") == "S2"

def test_nonexistent_metadata_returns_empty_dict(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")
    assert Prompt.get_metadata("nope", "v0001") == {}
