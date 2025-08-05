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
        return hashlib.sha256(text.encode()).hexdigest()

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
            last_text = existing_versions[-1].read_text()
            last_hash = cls._hash(last_text)

        latest_file.write_text(prompt)
        print(f"[Prompt] Updated latest.txt for '{name}'")

        if current_hash != last_hash:
            version_num = len(existing_versions) + 1
            version_file = versions_dir / f"v{version_num:04d}.txt"
            metadata_file = versions_dir / f"v{version_num:04d}.json"
            
            # Save prompt content
            version_file.write_text(prompt)
            
            # Prepare metadata
            commit_metadata = {
                "hash": current_hash,
                "timestamp": datetime.now().isoformat(),
                "version": f"v{version_num:04d}",
                "size": len(prompt.encode('utf-8')),
                "line_count": len(prompt.split('\n')),
                "previous_hash": last_hash,
                "metadata": metadata or {}
            }
            
            # Save metadata
            metadata_file.write_text(json.dumps(commit_metadata, indent=2))
            
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
        versions = sorted(f.name for f in versions_dir.glob("v*.txt"))
        print(f"[Prompt] Versions for '{name}':")
        
        for v in versions:
            if show_metadata:
                metadata_file = versions_dir / f"{v[:-4]}.json"  # Replace .txt with .json
                if metadata_file.exists():
                    try:
                        metadata = json.loads(metadata_file.read_text())
                        timestamp = datetime.fromisoformat(metadata['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                        hash_short = metadata['hash'][:8]
                        print(f"  - {v} ({timestamp}) [{hash_short}]")
                    except (json.JSONDecodeError, KeyError):
                        print(f"  - {v} [metadata error]")
                else:
                    print(f"  - {v} [no metadata]")
            else:
                print(f"  - {v}")
        return versions

    @classmethod
    def get_metadata(cls, name: str, version: str) -> dict:
        """Get metadata for a specific version"""
        versions_dir = cls.base_dir / name / "versions"
        metadata_file = versions_dir / f"{version[:-4] if version.endswith('.txt') else version}.json"
        
        if not metadata_file.exists():
            return {}
        
        try:
            return json.loads(metadata_file.read_text())
        except json.JSONDecodeError:
            return {}

    @classmethod
    def show_version_info(cls, name: str, version: str):
        """Show detailed information about a specific version"""
        metadata = cls.get_metadata(name, version)
        
        if not metadata:
            print(f"[Prompt] No metadata found for {name} {version}")
            return
        
        print(f"[Prompt] Version Info for {name} {version}:")
        print(f"  Hash: {metadata['hash']}")
        print(f"  Timestamp: {metadata['timestamp']}")
        print(f"  Size: {metadata['size']} bytes")
        print(f"  Lines: {metadata['line_count']}")
        if metadata.get('previous_hash'):
            print(f"  Previous Hash: {metadata['previous_hash']}")
        if metadata.get('metadata'):
            print(f"  Custom Metadata: {metadata['metadata']}")

    @classmethod
    def log(cls, name: str, limit: int = 10):
        """Show version history like git log"""
        versions_dir = cls.base_dir / name / "versions"
        if not versions_dir.exists():
            print(f"[Prompt] No versions found for '{name}'")
            return
        
        versions = sorted(versions_dir.glob("v*.txt"), reverse=True)[:limit]
        print(f"[Prompt] Version History for '{name}':")
        
        for version_file in versions:
            metadata_file = versions_dir / f"{version_file.stem}.json"
            if metadata_file.exists():
                try:
                    metadata = json.loads(metadata_file.read_text())
                    timestamp = datetime.fromisoformat(metadata['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                    hash_short = metadata['hash'][:8]
                    print("")
                    print(f"Version: {metadata['version']}")
                    print(f"Hash: {hash_short}")
                    print(f"Date: {timestamp}")
                    print(f"Size: {metadata['size']} bytes, {metadata['line_count']} lines")
                    if metadata.get('metadata'):
                        print(f"Metadata: {metadata['metadata']}")
                except (json.JSONDecodeError, KeyError):
                    print(f"  {version_file.name} [metadata error]")
            else:
                print(f"  {version_file.name} [no metadata]")

    @classmethod
    def get_prompt(cls, name: str, version: str = "latest") -> str:
        """Get prompt content for a specific version"""
        prompt_dir = cls.base_dir / name
        
        if version == "latest":
            prompt_file = prompt_dir / "latest.txt"
        else:
            # Handle both v0001.txt and v0001 formats
            version_name = version if version.endswith('.txt') else f"{version}.txt"
            prompt_file = prompt_dir / "versions" / version_name
        
        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt '{name}' version '{version}' not found")
        
        return prompt_file.read_text()

    @classmethod
    def format_prompt(cls, prompt_name: str, version: str = "latest", **kwargs) -> str:
        """Get prompt and format it with provided variables"""
        prompt_text = cls.get_prompt(prompt_name, version)
        return prompt_text.format(**kwargs) if kwargs else prompt_text

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
                    version_count = len(list(versions_dir.glob("v*.txt")))
                    overview_data[prompt_dir.name] = version_count
        print("[Prompt] Overview:")
        for name, count in overview_data.items():
            print(f"  - {name}: {count} version(s)")
        return overview_data
