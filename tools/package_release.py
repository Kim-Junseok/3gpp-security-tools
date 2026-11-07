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
parser.add_argument('--tag', default='v0.1.0-rc7')
parser.add_argument('--evidence', default='validation/shared-pdcp/windows')
args = parser.parse_args()
if not re.fullmatch(r'v\d+\.\d+\.\d+(?:-rc\d+)?', args.tag):
    parser.error('Use a version tag such as v0.1.0-rc7.')
for options in (['diff', '--quiet'], ['diff', '--cached', '--quiet']):
    subprocess.run(['git', *options], cwd=root, check=True)

def report(name):
    return json.loads((root / args.evidence / name).read_text(encoding='utf-8-sig'))

exe = root / 'dist/3GPP-Security-Tools.exe'
sha256 = hashlib.sha256(exe.read_bytes()).hexdigest()
official, gui, deployment = [report(name) for name in ('official-report.json', 'gui-report.json', 'deployment-report.json')]
if not (official['all_passed'] and official['required'] == official['passed'] == 135
        and len(official['cases']) == 135 and all(c['status'] == 'PASS' for c in official['cases'])
        and gui['total'] == gui['passed'] == len(gui['cases']) == 277
        and all(c['status'] == 'PASS' for c in gui['cases']) and deployment['exe_sha256'] == sha256
        and deployment['official_required'] == deployment['official_passed'] == 135
        and deployment['gui_total'] == deployment['gui_passed'] == 277
        and official['environment']['frozen'] and gui['environment']['frozen']):
    raise SystemExit('The EXE must match passing 135-case official and 277-case GUI evidence.')
build = report('build-info.json')
if any(r['environment']['commit'] != build['commit'] for r in (official, gui)):
    raise SystemExit('Official and GUI evidence must identify the same verified build.')
runtime_files = {str(p.relative_to(root)).replace('\\', '/')
                 for folder in ('src', 'testdata') for p in (root / folder).rglob('*')
                 if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'}
if runtime_files != {name for name in build['files'] if name.startswith(('src/', 'testdata/'))}:
    raise SystemExit('The source/testdata inventory differs from the verified EXE build.')
verified_files = {}
for name, expected_hash in build['files'].items():
    data = (root / name).read_bytes()
    variants = {'exact': data, 'LF': data.replace(b'\r\n', b'\n'),
                'CRLF': data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')}
    matching = next((kind for kind, value in variants.items() if hashlib.sha256(value).hexdigest() == expected_hash), None)
    if matching is None:
        raise SystemExit(f'Release input differs from the verified build: {name}')
    verified_files[name] = dict(build_sha256=expected_hash, matching_line_endings=matching)
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
commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
manifest = dict(tag=args.tag, release_commit=commit, verified_build_commit=build['commit'],
                exe_sha256=sha256, official_passed=135, windows_gui_passed=277,
                evidence=args.evidence, windows_environment=deployment['os'],
                build_input_verification=verified_files,
                limitations=['Windows 11 visual/DPI testing was not repeated for rc7.',
                             'COUNT is entered manually; RRC configuration and Manual Hex/SLRB prefix semantics are supplied by the user.',
                             'Fresh-PC/VM, mixed-DPI, Windows 10 and ARM64 testing remain unverified.'])
(dist / 'release-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
shutil.copy2(dist / 'release-manifest.json', stage / 'release-manifest.json')
(stage / 'RUNNING.txt').write_text(
    f'3GPP Security Tools {args.tag}\n\n'
    'Run 3GPP-Security-Tools.exe. No Python or additional library installation is required.\n'
    'The GUI is in English. README.md and docs/ are written in Korean.\n'
    'Choose Transmit or Receive, enable Ciphering and/or Integrity, and select algorithms independently.\n'
    'PDCP is the default mode. Its header source defaults to Automatic; the generated Hex is read-only.\n'
    'Choose the actual LTE/NR format, SN length and D/C when applicable. The low SN bits of COUNT form the header; HFN remains outside it.\n'
    'LTE SRB: 5-bit SN; LTE DRB: 7/12/15/18-bit SN; LTE SLRB: 16-bit SN and an actual 3-byte identity/type prefix.\n'
    'NR SRB: 12-bit SN; NR DRB: 12/18-bit SN. SRB and SLRB have no D/C field.\n'
    'D/C=0 is a Control PDU and cannot use this automatic Data PDU protection pipeline.\n'
    'LTE DRB supports P for DL/18-bit SN and AILC for UL/12-bit SN. Inactive flags are retained but not applied.\n'
    'Manual Hex remains available for captured/other headers and retains its own value when switching to and from Automatic.\n'
    'If SDAP header present is selected, enter exactly one byte in its separate Hex field. SDAP is never regenerated when UL/DL changes.\n'
    'Payload input/output excludes both headers. Integrity covers PDCP header + optional SDAP header + plaintext payload.\n'
    'Ciphering covers Payload + MAC-I only; both headers remain outside Ciphering.\n'
    'Raw mode preserves direct algorithm-input calculations without separate headers.\n'
    'COUNT is entered manually and used in full by the security primitives. RRC bearer configuration and manual header/prefix semantics are not decoded.\n'
    'Algorithms 1-3 require 128-bit keys; algorithms 4-6 require 256-bit keys. Algorithm 0 is Null.\n'
    'COUNT accepts Decimal (default), Hex, or Bit. BEARER is decimal; DIRECTION is 0=UL or 1=DL.\n'
    'Algorithms 4-6 use a 48-bit EXTRA_IV; Integrity 4-6 accepts a 4-16-byte MAC-I.\n'
    'Both tabs share mode, radio settings, keys, all PDCP header values/generation settings, and SDAP presence/Hex. Only payload text stays separate.\n'
    'For receive with Integrity enabled, Input data includes the trailing MAC-I. There is no separate MAC field.\n'
    'With Ciphering enabled too, enter the ciphertext of Data + MAC-I. Use the same MAC length as the sender.\n'
    'Lengths show exact bits and bytes, e.g. 128 bit (16 bytes) or 43 bit (5 bytes + 3 bits); no padding is added.\n'
    'Hex output uses uppercase letters and spaces between bytes. Use the right scrollbar on short screens.\n'
    'Existing Markdown documentation is preserved from rc5; use this file and release-manifest.json for rc7 changes and scope.\n\n'
    f"Verified EXE: {official['passed']}/{official['required']} official vectors and {gui['passed']}/{gui['total']} GUI checks.\n"
    'The 135 vectors comprise 36 legacy, 72 NEA/NIA, and 27 primitive cases.\n'
    f"Verified Windows environment: {deployment['os']['Caption']} ({deployment['os']['Version']}, {deployment['os']['OSArchitecture']}).\n"
    f"Deployment test scope: {deployment['scope']}\n"
    'Windows 11 visual/DPI testing was not repeated for rc7.\n'
    'Fresh-PC/VM, mixed-DPI monitor transitions, Windows 10, and ARM64 testing remain unverified.\n'
    f'EXE SHA-256: {sha256}\n', encoding='utf-8')
zip_path = dist / (name + '.zip')
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(stage.rglob('*')):
        if path.is_file():
            archive.write(path, str(path.relative_to(stage)))
source = dist / f'3gpp-security-tools-{version}-source.zip'
subprocess.run(['git', 'archive', '--format=zip', '--prefix=3gpp-security-tools/', '--output', str(source), 'HEAD'], cwd=root, check=True)
files = [exe, zip_path, source, dist / 'release-manifest.json']
(dist / 'SHA256SUMS.txt').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in files))
for path in files:
    print(path.name, path.stat().st_size)
with zipfile.ZipFile(zip_path) as archive:
    if hashlib.sha256(archive.read(exe.name)).hexdigest() != sha256:
        raise SystemExit('Packaged EXE differs from the verified standalone EXE.')
    if archive.testzip() is not None:
        raise SystemExit('Windows ZIP integrity check failed.')
with zipfile.ZipFile(source) as archive:
    if archive.testzip() is not None:
        raise SystemExit('Source ZIP integrity check failed.')
print('Release packaging checks passed; verified build inputs:', len(verified_files))
