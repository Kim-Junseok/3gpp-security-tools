"""Expose validation results in CI logs as well as downloadable artifacts."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
for path in sorted((root / 'validation/256-bit').rglob('*.json')):
    if path.name not in ('official-report.json', 'gui-report.json', 'integration-report.json',
                         'deployment-report.json', 'build-info.json', 'answers.json'):
        continue
    # These reports contain public test vectors and runtime/build metadata only.
    obj = json.loads(path.read_text(encoding='utf-8-sig'))
    print('VALIDATION_EVIDENCE ' + json.dumps(dict(path=path.relative_to(root).as_posix(), report=obj), separators=(',', ':')))
