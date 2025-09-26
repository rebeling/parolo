import json
from parolo import Prompt

def test_single_prompt_version(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    Prompt.create("task", prompt="Write a poem about the sea.")
    versions = Prompt.list_versions("task")

    assert versions == ["v0001.txt"]
    assert (Prompt.base_dir / "task" / "latest.txt").read_text() == "Write a poem about the sea."

    # Check metadata file was created
    metadata_file = Prompt.base_dir / "task" / "versions" / "v0001.json"
    assert metadata_file.exists()

    # Check metadata content
    metadata = json.loads(metadata_file.read_text())
    assert metadata['version'] == 'v0001'
    assert metadata['size'] == len("Write a poem about the sea.".encode('utf-8'))
    assert metadata['line_count'] == 1
    assert 'hash' in metadata
    assert 'timestamp' in metadata

def test_no_duplicate_version(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    Prompt.create("task", prompt="Repeat after me.")
    Prompt.create("task", prompt="Repeat after me.")  # Should not trigger new version

    versions = Prompt.list_versions("task")
    assert len(versions) == 1

def test_multiple_versions(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    Prompt.create("task", prompt="Version 1")
    Prompt.create("task", prompt="Version 2")
    Prompt.create("task", prompt="Version 3")

    versions = Prompt.list_versions("task")
    assert versions == ["v0001.txt", "v0002.txt", "v0003.txt"]
    assert (Prompt.base_dir / "task" / "latest.txt").read_text() == "Version 3"

    # Check all metadata files were created
    for i in range(1, 4):
        metadata_file = Prompt.base_dir / "task" / "versions" / f"v{i:04d}.json"
        assert metadata_file.exists()

        metadata = json.loads(metadata_file.read_text())
        assert metadata['version'] == f'v{i:04d}'
        assert metadata['size'] == len(f"Version {i}".encode('utf-8'))

        # Check previous_hash is set correctly
        if i > 1:
            assert metadata['previous_hash'] is not None
        else:
            assert metadata['previous_hash'] is None

def test_overview_counts(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    Prompt.create("alpha", prompt="A")
    Prompt.create("beta", prompt="B")
    Prompt.create("beta", prompt="C")

    summary = Prompt.overview()
    assert summary == {"alpha": 1, "beta": 2}

def test_list_versions_empty(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    versions = Prompt.list_versions("nonexistent")
    assert versions == []

def test_metadata_creation(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    # Create prompt with custom metadata
    custom_meta = {"author": "Test", "category": "demo"}
    Prompt.create("meta_test", "Test prompt", metadata=custom_meta)

    # Check metadata was stored correctly
    metadata = Prompt.get_metadata("meta_test", "v0001")
    assert metadata["metadata"] == custom_meta
    assert metadata["version"] == "v0001"
    assert metadata["size"] == len("Test prompt".encode('utf-8'))
    assert metadata["line_count"] == 1
    assert "hash" in metadata
    assert "timestamp" in metadata

def test_get_metadata_nonexistent(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    # Test getting metadata for nonexistent prompt
    metadata = Prompt.get_metadata("nonexistent", "v0001")
    assert metadata == {}

def test_previous_hash_tracking(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    # Create first version
    Prompt.create("hash_test", "First version")
    first_metadata = Prompt.get_metadata("hash_test", "v0001")

    # Create second version
    Prompt.create("hash_test", "Second version")
    second_metadata = Prompt.get_metadata("hash_test", "v0002")

    # Check previous hash tracking
    assert first_metadata["previous_hash"] is None
    assert second_metadata["previous_hash"] == first_metadata["hash"]
    assert second_metadata["hash"] != first_metadata["hash"]

def test_get_prompt_latest(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    # Create a prompt
    Prompt.create("test_get", "Hello {name}!")

    # Get latest version
    prompt = Prompt.get_prompt("test_get")
    assert prompt == "Hello {name}!"

    # Get latest explicitly
    prompt_latest = Prompt.get_prompt("test_get", version="latest")
    assert prompt_latest == "Hello {name}!"

def test_get_prompt_specific_version(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    # Create multiple versions
    Prompt.create("version_test", "Version 1")
    Prompt.create("version_test", "Version 2")

    # Get specific versions
    v1 = Prompt.get_prompt("version_test", version="v0001")
    v2 = Prompt.get_prompt("version_test", version="v0002")

    assert v1 == "Version 1"
    assert v2 == "Version 2"

    # Test with .txt extension
    v1_txt = Prompt.get_prompt("version_test", version="v0001.txt")
    assert v1_txt == "Version 1"

def test_get_prompt_nonexistent(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    # Test nonexistent prompt
    try:
        Prompt.get_prompt("nonexistent")
        assert False, "Should have raised FileNotFoundError"
    except FileNotFoundError as e:
        assert "not found" in str(e)

def test_format_prompt(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    # Create a prompt with template variables
    Prompt.create("greeting", "Hello {name}! Welcome to {place}.")

    # Format with variables
    formatted = Prompt.format_prompt("greeting", name="Alice", place="Wonderland")
    assert formatted == "Hello Alice! Welcome to Wonderland."

    # Format without variables (should return original)
    unformatted = Prompt.format_prompt("greeting")
    assert unformatted == "Hello {name}! Welcome to {place}."

def test_format_prompt_specific_version(tmp_path):
    Prompt.set_base_dir(tmp_path / "prompts")

    # Create multiple versions
    Prompt.create("evolving", "Hello {name}!")
    Prompt.create("evolving", "Greetings {name}! How are you?")

    # Format specific versions
    v1_formatted = Prompt.format_prompt("evolving", version="v0001", name="Bob")
    v2_formatted = Prompt.format_prompt("evolving", version="v0002", name="Bob")

    assert v1_formatted == "Hello Bob!"
    assert v2_formatted == "Greetings Bob! How are you?"
