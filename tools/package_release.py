"""Assemble a release from a verified Windows EXE and committed evidence."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--tag', default='v0.1.0-rc4')
parser.add_argument('--evidence', default='validation/rc4/windows')
args = parser.parse_args()
if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-rc\d+)?', args.tag):
    parser.error('Use a version tag such as v0.1.0-rc4.')
for options in (['diff', '--quiet'], ['diff', '--cached', '--quiet']):
    subprocess.run(['git', *options], cwd=root, check=True)

def report(name):
    return json.loads((root / args.evidence / name).read_text(encoding='utf-8-sig'))

exe = root / 'dist/3GPP-Security-Tools.exe'
sha256 = hashlib.sha256(exe.read_bytes()).hexdigest()
official, gui, deployment = [report(name) for name in ('official-report.json', 'gui-report.json', 'deployment-report.json')]
if not (official['all_passed'] and official['required'] == official['passed'] == 135
        and gui['total'] == gui['passed'] == 199 and deployment['exe_sha256'] == sha256
        and official['environment']['frozen'] and gui['environment']['frozen']):
    raise SystemExit('The EXE must match passing 135-case official and 199-case GUI evidence.')
tracked = subprocess.check_output(['git', 'ls-files', 'validation'], cwd=root, text=True).splitlines()
if (Path(args.evidence) / 'official-report.json').as_posix() not in tracked:
    raise SystemExit('Commit the release evidence before packaging the source snapshot.')

version = args.tag.removeprefix('v')
name = f'3GPP-Security-Tools-{version}-windows-x64'
dist = root / 'dist'
stage = root / '.build' / name
if stage.exists():
    shutil.rmtree(stage)
stage.mkdir(parents=True)
shutil.copy2(exe, stage / exe.name)
shutil.copy2(root / 'README.md', stage / 'README.md')
(stage / 'docs').mkdir()
for document in ('FOLLOW_UP.md', 'RELEASE_NOTES.md', 'SOURCES.md', 'VALIDATION.md'):
    shutil.copy2(root / 'docs' / document, stage / 'docs' / document)
for relative in tracked:
    target = stage / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / relative, target)
shutil.copytree(root / 'packaging/licenses', stage / 'licenses')
(stage / 'RUNNING.txt').write_text(
    f'3GPP Security Tools {args.tag}\n\n'
    'Run 3GPP-Security-Tools.exe. No Python or additional library installation is required.\n'
    'The GUI is in English. README.md and docs/ are written in Korean.\n'
    'Choose Transmit or Receive, enable Ciphering and/or Integrity, and select algorithms independently.\n'
    'Algorithms 1-3 require 128-bit keys; algorithms 4-6 require 256-bit keys. Algorithm 0 is Null.\n'
    'COUNT accepts Decimal (default), Hex, or Bit. BEARER is decimal; DIRECTION is 0=UL or 1=DL.\n'
    'Algorithms 4-6 use a 48-bit EXTRA_IV; Integrity 4-6 accepts a 4-16-byte MAC-I.\n'
    'Both tabs share the radio settings and keys. Input data stays separate for each tab.\n'
    'Hex output uses uppercase letters and spaces between bytes. Use the right scrollbar on short screens.\n\n'
    f"Verified EXE: {official['passed']}/{official['required']} official vectors and {gui['passed']}/{gui['total']} GUI checks.\n"
    'The 135 vectors comprise 36 legacy, 72 NEA/NIA, and 27 primitive cases.\n'
    'This EXE was tested on Windows 11 x64 with the development runtime isolated.\n'
    'Fresh-PC/VM, mixed-DPI monitor transitions, Windows 10, and ARM64 testing remain unverified.\n'
    f'EXE SHA-256: {sha256}\n', encoding='utf-8')
zip_path = dist / (name + '.zip')
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(stage.rglob('*')):
        if path.is_file():
            archive.write(path, str(path.relative_to(stage)))
source = dist / f'3gpp-security-tools-{version}-source.zip'
subprocess.run(['git', 'archive', '--format=zip', '--prefix=3gpp-security-tools/', '--output', str(source), 'HEAD'], cwd=root, check=True)
files = [exe, zip_path, source]
(dist / 'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files))
for path in files:
    print(path.name, path.stat().st_size)
