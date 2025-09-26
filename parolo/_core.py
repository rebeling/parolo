from __future__ import annotations
import os, json, tempfile, hashlib
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional

# Base dir (same default as before)
BASE_DIR = Path(os.environ.get("PAROLO_HOME", Path.home() / ".parolo" / "prompts")).resolve()

# Jinja2 is optional: class API stays on str.format; function render() uses Jinja if present
try:
    from jinja2 import Environment, StrictUndefined, meta
    _JENV = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    _JINJA_OK = True
except Exception:
    _JENV = None
    _JINJA_OK = False

# -------- helpers --------
def set_base_dir(path: str | Path) -> None:
    global BASE_DIR
    BASE_DIR = Path(path).resolve()

def _dir(name: str) -> Path:          return BASE_DIR / name
def _latest(name: str) -> Path:       return _dir(name) / "latest.txt"
def _vdir(name: str) -> Path:         return _dir(name) / "versions"
def _vfiles(name: str) -> List[Path]: return sorted(_vdir(name).glob("v*.txt"))

def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", delete=False, dir=path.parent, encoding="utf-8") as tf:
        tf.write(text)
        tmp = Path(tf.name)
    os.replace(tmp, path)

def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def _now_iso() -> str:
    return datetime.now().isoformat()

# -------- core I/O (compatible layout) --------
def put(name: str, text: str, *, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Save live prompt to latest.txt (atomically).
    Write a new versions/vNNNN.txt + vNNNN.json only if content changed.
    """
    latest = _latest(name)
    vdir = _vdir(name); vdir.mkdir(parents=True, exist_ok=True)

    existing = _vfiles(name)
    last_hash = _sha256(existing[-1].read_text(encoding="utf-8")) if existing else None
    cur_hash = _sha256(text)

    _atomic_write_text(latest, text)

    if not existing or cur_hash != last_hash:
        next_n = (int(existing[-1].stem[1:]) + 1) if existing else 1
        ver = f"v{next_n:04d}"
        _atomic_write_text(vdir / f"{ver}.txt", text)

        meta_obj = {
            "version": ver,
            "hash": cur_hash,
            "timestamp": _now_iso(),
            "size": len(text.encode("utf-8")),
            "line_count": len(text.splitlines()),
            "previous_hash": last_hash,
            "metadata": metadata or {},
        }
        # best-effort: list Jinja variables to help debuggability
        if _JINJA_OK:
            try:
                ast = _JENV.parse(text)
                meta_obj["jinja_variables"] = sorted(list(meta.find_undeclared_variables(ast)))
            except Exception:
                pass

        _atomic_write_text(vdir / f"{ver}.json", json.dumps(meta_obj, indent=2))
        return {"version": ver, "hash": cur_hash, "size": meta_obj["size"], "lines": meta_obj["line_count"]}
    else:
        return {"version": existing[-1].stem, "hash": cur_hash, "size": len(text.encode("utf-8")),
                "lines": len(text.splitlines())}

def get(name: str) -> str:
    return _latest(name).read_text(encoding="utf-8")

def get_version(name: str, version: str) -> str:
    vname = version if version.endswith(".txt") else f"{version}.txt"
    p = _vdir(name) / vname
    if not p.exists():
        raise FileNotFoundError(f"{name} {version} not found")
    return p.read_text(encoding="utf-8")

def meta_version(name: str, version: str) -> Dict[str, Any]:
    stem = version[:-4] if version.endswith(".txt") else version
    p = _vdir(name) / f"{stem}.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}

# -------- listing --------
def list_versions(name: str, *, with_meta: bool = False):
    files = _vfiles(name)
    if not with_meta:
        return [p.name for p in files]
    out = []
    for p in files:
        m = meta_version(name, p.stem)
        out.append({
            "file": p.name,
            "version": p.stem,
            "timestamp": m.get("timestamp"),
            "hash": m.get("hash"),
            "size": m.get("size"),
            "line_count": m.get("line_count"),
            "jinja_variables": m.get("jinja_variables"),
        })
    return out

def list_all(*, with_meta: bool = True) -> List[Dict[str, Any]]:
    if not BASE_DIR.exists():
        return []
    out: List[Dict[str, Any]] = []
    for entry in sorted(BASE_DIR.iterdir()):
        if not entry.is_dir():
            continue
        name = entry.name
        latest = entry / "latest.txt"
        vfiles = _vfiles(name)
        info = {"name": name, "versions": len(vfiles), "has_latest": latest.exists()}
        if with_meta and vfiles:
            m = meta_version(name, vfiles[-1].stem)
            info.update({
                "latest_version": vfiles[-1].stem,
                "hash": m.get("hash"),
                "timestamp": m.get("timestamp"),
                "size": m.get("size"),
                "line_count": m.get("line_count"),
            })
        out.append(info)
    return out

# -------- hot-reload token --------
def token(name: str) -> int:
    try:
        return _latest(name).stat().st_mtime_ns
    except FileNotFoundError:
        return 0

# -------- Jinja2 rendering (function API only) --------
def template(prompt_id: str):
    """Compile current prompt as a Jinja2 template (StrictUndefined)."""
    return _JENV.from_string(get(prompt_id))

def render(prompt_id: str, **context) -> str:
    """Render current prompt with Jinja2 (StrictUndefined)."""
    return template(prompt_id).render(**context)

def render_version(prompt_id: str, version: str, **context) -> str:
    return _JENV.from_string(get_version(prompt_id, version)).render(**context)

def jinja_variables(name: str) -> List[str]:
    if not _JINJA_OK:
        return []
    try:
        ast = _JENV.parse(get(name))
        return sorted(list(meta.find_undeclared_variables(ast)))
    except Exception:
        return []
