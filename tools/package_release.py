"""Assemble the tested Windows executable with notices and evidence."""

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
dist = root / "dist"
name = "3GPP-Security-Tools-0.1.0-windows-x64"
stage = root / ".build" / name
if stage.exists():
    shutil.rmtree(stage)
stage.mkdir(parents=True)
shutil.copy2(dist / "3GPP-Security-Tools.exe", stage / "3GPP-Security-Tools.exe")
shutil.copy2(root / "README.md", stage / "README.md")
(stage / "docs").mkdir()
for document in ("FOLLOW_UP.md", "RELEASE_NOTES.md", "SOURCES.md", "VALIDATION.md"):
    shutil.copy2(root / "docs" / document, stage / "docs" / document)
shutil.copytree(root / "validation/v0.1", stage / "validation/v0.1", dirs_exist_ok=True)
shutil.copytree(root / "validation/gui-update", stage / "validation/gui-update", dirs_exist_ok=True)
shutil.copytree(root / "packaging/licenses", stage / "licenses", dirs_exist_ok=True)
gui_report = json.loads((root / "validation/gui-update/windows/gui-report.json").read_text(encoding="utf-8"))
(stage / "실행방법.txt").write_text(
    "3GPP-Security-Tools.exe를 실행하세요. Python이나 별도 라이브러리를 설치할 필요가 없습니다.\n"
    "송신/수신 탭에서 Ciphering과 Integrity를 각각 선택하고 활성 필드를 입력하세요.\n"
    "COUNT는 Decimal(기본)·Hex·Bit 중 선택합니다. BEARER는 10진수입니다.\n"
    "송신/수신 탭의 키·알고리즘·COUNT·BEARER·DIRECTION 설정은 함께 유지됩니다.\n"
    "Hex는 대문자와 byte 사이 공백으로 표시합니다. Hex/Bit 입력 길이는 자동 계산합니다.\n"
    f"Windows 11 Home x64에서 실제 실행했습니다. 공식 36/36, GUI widget {gui_report['passed']}/{gui_report['total']} PASS입니다.\n"
    "새 Windows PC/VM, Windows 10, ARM64는 검증하지 않았습니다.\n"
    "세부 사용법과 정확한 검증 범위는 README.md 및 docs/VALIDATION.md를 참조하세요.\n",
    encoding="utf-8-sig")
zip_path = dist / (name + ".zip")
with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(stage.rglob("*")):
        if path.is_file():
            archive.write(path, str(path.relative_to(stage)))
source = dist / "3gpp-security-tools-0.1.0-source.zip"
subprocess.run(["git", "archive", "--format=zip", "--prefix=3gpp-security-tools/", "--output", str(source), "HEAD"], cwd=root, check=True)
files = [dist / "3GPP-Security-Tools.exe", zip_path, source]
(dist / "SHA256SUMS.txt").write_text("".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in files))
for path in files:
    print(path.name, path.stat().st_size)
