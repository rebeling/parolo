import os
import subprocess
import sys
import tempfile
import pytest
from pathlib import Path

pytestmark = pytest.mark.slow

build = pytest.importorskip("build")

def test_build_and_import_wheel(tmp_path):
    # Build dist into a temp dir
    dist_dir = tmp_path / "dist"
    dist_dir.mkdir()
    subprocess.run([sys.executable, "-m", "build", "--outdir", str(dist_dir)], check=True)

    # Find the wheel
    wheels = list(dist_dir.glob("*.whl"))
    assert wheels, "No wheel built"
    wheel = wheels[0]

    # Create a throwaway venv and install the wheel
    venv_dir = tmp_path / "venv"
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
    pip = venv_dir / ("Scripts" if os.name == "nt" else "bin") / "pip"
    py  = venv_dir / ("Scripts" if os.name == "nt" else "bin") / "python"

    subprocess.run([str(pip), "install", str(wheel)], check=True)

    # Sanity import test in the clean env
    code = "from parolo import Prompt; print(Prompt)"
    subprocess.run([str(py), "-c", code], check=True)
