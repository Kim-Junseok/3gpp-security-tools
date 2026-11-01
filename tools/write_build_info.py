import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]


def git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


files = {str(p.relative_to(root)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
         for folder in ["src", "testdata", "packaging"] for p in sorted((root / folder).rglob("*"))
         if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}
stamp = root / ".build/source-stamp.json"
source_stamp = json.loads(stamp.read_text()) if stamp.exists() else {}
data = {"commit": git("rev-parse", "HEAD") or source_stamp.get("commit"), "dirty": bool(git("status", "--porcelain")) or source_stamp.get("dirty", False),
        "files": files, "python": sys.version}
(root / "build-info.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
