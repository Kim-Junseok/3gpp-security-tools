"""Record WSL Git identity before a Windows build without Windows Git."""
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
dest = root / ".build/source-stamp.json"
dest.parent.mkdir(exist_ok=True)
dest.write_text(json.dumps({
    "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip(),
    "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True))
}, indent=2) + "\n")
