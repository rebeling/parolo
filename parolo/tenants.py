# parolo/tenants.py
from __future__ import annotations
from datetime import datetime
from typing import Callable, Optional, Dict, Any, List

# We rely on the namespaced API (parolo.prompts)
from . import prompts

DEFAULT_SEMVER_BASE = "1.0."

def key(tenant_id: str, agent_id: str) -> str:
    """Build a stable prompt id like 'tenant_agent'."""
    return f"{tenant_id}_{agent_id}"

def _find_parolo_version_by_semver(prompt_id: str, semver: str) -> Optional[str]:
    """Find vNNNN for a given semver in metadata."""
    try:
        versions = prompts.versions(prompt_id, with_meta=True)
    except Exception:
        return None
    for entry in versions:
        v = entry["version"]          # e.g. 'v0003'
        meta = prompts.meta(prompt_id, v)
        if meta and meta.get("metadata", {}).get("semver") == semver:
            return v
    return None

def list_semvers(tenant_id: str, agent_id: str) -> List[str]:
    """List semvers from metadata; if missing, synthesize 1.0.<i>."""
    pid = key(tenant_id, agent_id)
    try:
        rich = prompts.versions(pid, with_meta=True)
    except Exception:
        return []
    out: List[str] = []
    for i, entry in enumerate(rich):
        meta = prompts.meta(pid, entry["version"]) or {}
        sv = (meta.get("metadata") or {}).get("semver")
        out.append(sv if sv else f"{DEFAULT_SEMVER_BASE}{i}")
    return out

def latest_semver(tenant_id: str, agent_id: str) -> Optional[str]:
    semvers = list_semvers(tenant_id, agent_id)
    return semvers[-1] if semvers else None

def save(
    tenant_id: str,
    agent_id: str,
    text: str,
    *,
    semver: Optional[str] = None,
    extra_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, str]:
    """Save prompt text; attach semver in metadata (auto if not provided)."""
    pid = key(tenant_id, agent_id)

    # Auto semver if not provided: 1.0.<patch> where patch=len(versions)
    versions = prompts.versions(pid)
    if semver is None:
        patch = len(versions)  # new version index (0-based)
        semver = f"{DEFAULT_SEMVER_BASE}{patch}"

    meta = {
        "tenant_id": tenant_id,
        "agent_id": agent_id,
        "created_at": datetime.utcnow().isoformat(),
        "semver": semver,
    }
    if extra_metadata:
        meta.update(extra_metadata)

    info = prompts.save(pid, text, metadata=meta)  # writes latest.txt + vNNNN if changed
    return {"semver": semver, "parolo_version": info["version"]}

def read(
    tenant_id: str,
    agent_id: str,
    *,
    semver: Optional[str] = None,
    fallback: Optional[Callable[[], Optional[str]]] = None,
) -> str:
    """Read latest or specific semver. Optional fallback() returns a string."""
    pid = key(tenant_id, agent_id)
    try:
        if semver:
            v = _find_parolo_version_by_semver(pid, semver)
            if v:
                return prompts.read_version(pid, v)
            raise FileNotFoundError(f"{pid} semver {semver} not found")
        return prompts.read(pid)
    except Exception:
        if fallback:
            fb = fallback()
            if fb is not None:
                return fb
        raise

def ensure_initial(
    tenant_id: str,
    agent_id: str,
    text: str,
    semver: str = "1.0.0",
    *,
    overwrite: bool = False,
) -> Optional[str]:
    """Create initial version if none exists (or overwrite if asked)."""
    pid = key(tenant_id, agent_id)
    try:
        already = prompts.versions(pid)
        if already and not overwrite:
            return None
    except Exception:
        pass
    info = save(tenant_id, agent_id, text, semver=semver)
    return info["semver"]

# Optional tiny cache for hot paths
_cache: Dict[str, Dict[str, Any]] = {}
def read_cached(tenant_id: str, agent_id: str) -> str:
    pid = key(tenant_id, agent_id)
    t = prompts.token(pid)
    e = _cache.get(pid)
    if e and e["t"] == t:
        return e["text"]
    txt = prompts.read(pid)
    _cache[pid] = {"t": t, "text": txt}
    return txt
