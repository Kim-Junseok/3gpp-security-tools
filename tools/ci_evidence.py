"""Expose validation results in CI logs as well as downloadable artifacts."""

import argparse
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--root', default='validation/256-bit')
args = p.parse_args()
for path in sorted((root / args.root).rglob('*.json')):
    if path.name not in ('official-report.json', 'gui-report.json', 'integration-report.json',
                         'deployment-report.json', 'build-info.json', 'answers.json'):
        continue
    # These reports contain public test vectors and runtime/build metadata only.
    obj = json.loads(path.read_text(encoding='utf-8-sig'))
    text = json.dumps(obj, separators=(',', ':'))
    chunks = [text[n:n + 4000] for n in range(0, len(text), 4000)]
    for part, chunk in enumerate(chunks):
        print('VALIDATION_EVIDENCE ' + json.dumps(dict(path=path.relative_to(root).as_posix(),
              part=part, total=len(chunks), data=chunk), separators=(',', ':')))
