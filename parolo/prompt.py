from __future__ import annotations
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path

class Prompt:
    # Default base_dir is relative to where this file lives
    base_dir = Path(
        os.environ.get("PAROLO_HOME", Path.home() / ".parolo" / "prompts")
    )

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @classmethod
    def set_base_dir(cls, path: str | Path):
        cls.base_dir = Path(path).resolve()

    @classmethod
    def create(cls, name: str, prompt: str, metadata: dict = None):
        prompt_dir = cls.base_dir / name
        versions_dir = prompt_dir / "versions"
        latest_file = prompt_dir / "latest.txt"
        versions_dir.mkdir(parents=True, exist_ok=True)

        current_hash = cls._hash(prompt)

        # Compare to latest version hash
        existing_versions = sorted(versions_dir.glob("v*.txt"))
        last_hash = None
        if existing_versions:
            last_text = existing_versions[-1].read_text(encoding="utf-8")
            last_hash = cls._hash(last_text)

        # Always refresh latest.txt
        latest_file.write_text(prompt, encoding="utf-8")
        print(f"[Prompt] Updated latest.txt for '{name}'")

        if (not existing_versions) or (current_hash != last_hash):
            version_num = len(existing_versions) + 1
            version_file = versions_dir / f"v{version_num:04d}.txt"
            metadata_file = versions_dir / f"v{version_num:04d}.json"

            # Save prompt content
            version_file.write_text(prompt, encoding="utf-8")

            # Prepare metadata
            commit_metadata = {
                "hash": current_hash,
                "timestamp": datetime.now().isoformat(),
                "version": f"v{version_num:04d}",
                "size": len(prompt.encode("utf-8")),
                "line_count": len(prompt.splitlines()),
                "previous_hash": last_hash,  # None on first version
                "metadata": metadata or {},
            }

            # Save metadata
            metadata_file.write_text(json.dumps(commit_metadata, indent=2), encoding="utf-8")

            print(f"[Prompt] New version saved: {version_file}")
            print(f"[Prompt] Metadata saved: {metadata_file}")
        else:
            print("[Prompt] No changes detected — no new version created.")

    @classmethod
    def list_versions(cls, name: str, show_metadata: bool = False) -> list:
        versions_dir = cls.base_dir / name / "versions"
        if not versions_dir.exists():
            print(f"[Prompt] No versions found for '{name}'")
            return []
        files = sorted(versions_dir.glob("v*.txt"))
        versions = [f.name for f in files]  # ensure 'v0001.txt' shape
        print(f"[Prompt] Versions for '{name}':")
        if show_metadata:
            for f in files:
                mfile = versions_dir / f"{f.stem}.json"
                if mfile.exists():
                    try:
                        metadata = json.loads(mfile.read_text(encoding="utf-8"))
                        ts = datetime.fromisoformat(metadata["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                        h = metadata["hash"][:8]
                        print(f"  - {f.name} ({ts}) [{h}]")
                    except Exception:
                        print(f"  - {f.name} [metadata error]")
                else:
                    print(f"  - {f.name} [no metadata]")
        else:
            for v in versions:
                print(f"  - {v}")
        return versions

    @classmethod
    def get_metadata(cls, name: str, version: str) -> dict:
        """Get metadata for a specific version; accepts 'v0001' or 'v0001.txt'."""
        versions_dir = cls.base_dir / name / "versions"
        stem = version[:-4] if version.endswith(".txt") else version
        metadata_file = versions_dir / f"{stem}.json"
        if not metadata_file.exists():
            return {}
        try:
            return json.loads(metadata_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    @classmethod
    def show_version_info(cls, name: str, version: str):
        metadata = cls.get_metadata(name, version)
        if not metadata:
            print(f"[Prompt] No metadata found for {name} {version}")
            return
        print(f"[Prompt] Version Info for {name} {version}:")
        print(f"  Hash: {metadata['hash']}")
        print(f"  Timestamp: {metadata['timestamp']}")
        print(f"  Size: {metadata['size']} bytes")
        print(f"  Lines: {metadata['line_count']}")
        if metadata.get("previous_hash"):
            print(f"  Previous Hash: {metadata['previous_hash']}")
        if metadata.get("metadata"):
            print(f"  Custom Metadata: {metadata['metadata']}")

    @classmethod
    def log(cls, name: str, limit: int = 10):
        versions_dir = cls.base_dir / name / "versions"
        if not versions_dir.exists():
            print(f"[Prompt] No versions found for '{name}'")
            return
        files = sorted(versions_dir.glob("v*.txt"), reverse=True)[:limit]
        print(f"[Prompt] Version History for '{name}':")
        for f in files:
            mfile = versions_dir / f"{f.stem}.json"
            if mfile.exists():
                try:
                    metadata = json.loads(mfile.read_text(encoding="utf-8"))
                    ts = datetime.fromisoformat(metadata["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                    h = metadata["hash"][:8]
                    print("")
                    print(f"Version: {metadata['version']}")
                    print(f"Hash: {h}")
                    print(f"Date: {ts}")
                    print(f"Size: {metadata['size']} bytes, {metadata['line_count']} lines")
                    if metadata.get("metadata"):
                        print(f"Metadata: {metadata['metadata']}")
                except Exception:
                    print(f"  {f.name} [metadata error]")
            else:
                print(f"  {f.name} [no metadata]")

    @classmethod
    def get_prompt(cls, name: str, version: str = "latest") -> str:
        prompt_dir = cls.base_dir / name
        if version == "latest":
            prompt_file = prompt_dir / "latest.txt"
        else:
            version_name = version if version.endswith(".txt") else f"{version}.txt"
            prompt_file = prompt_dir / "versions" / version_name
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt '{name}' version '{version}' not found")
        return prompt_file.read_text(encoding="utf-8")

    @classmethod
    def format_prompt(cls, prompt_name: str, version: str = "latest", **kwargs) -> str:
        text = cls.get_prompt(prompt_name, version)
        return text.format(**kwargs) if kwargs else text

    @classmethod
    def overview(cls) -> dict:
        overview_data = {}
        if not cls.base_dir.exists():
            print(f"[Prompt] Base directory '{cls.base_dir}' does not exist.")
            return overview_data
        for prompt_dir in cls.base_dir.iterdir():
            if prompt_dir.is_dir():
                versions_dir = prompt_dir / "versions"
                if versions_dir.exists():
                    count = len(list(versions_dir.glob("v*.txt")))
                    overview_data[prompt_dir.name] = count
        print("[Prompt] Overview:")
        for name, count in overview_data.items():
            print(f"  - {name}: {count} version(s)")
        return overview_data
