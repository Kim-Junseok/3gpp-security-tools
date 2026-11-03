"""Fixed official Release 20 inventory, separate from legacy's 36 cases."""

from collections import Counter
import hashlib
import json
from pathlib import Path

from .algorithms import nea_nia, snow5g, zuc256
from .bits import Bits
from .core import cipher, mac
from .errors import VectorError

REQUIRED = {**{f'{kind}{a}': 12 for a in (4, 5, 6) for kind in ('NEA', 'NIA')},
            'POLYVAL241': 6, 'SNOW5G': 3, 'POLYVAL244': 6, 'AES256': 3, 'POLYVAL247': 6, 'ZUC256': 3}


def calculate(case, inp, exp):
    suite = case.rsplit('-', 1)[0]
    states = []
    if suite.startswith(('NEA', 'NIA')):
        args = (inp['algorithm'], bytes.fromhex(inp['key']), inp['count'], inp['bearer'], inp['direction'],
                Bits(bytes.fromhex(inp['buffer_hex']), inp['bit_length']))
        options = dict(extra_iv=bytes.fromhex(inp['extra_iv']))
        if suite.startswith('NIA'):
            options['mac_bytes'] = inp['mac_bytes']
        actual = (cipher if suite.startswith('NEA') else mac)(*args, **options)
    elif suite.startswith('POLYVAL'):
        value = nea_nia.pdot(int.from_bytes(bytes.fromhex(inp['a']), 'little'),
                            int.from_bytes(bytes.fromhex(inp['b']), 'little'))
        actual = Bits(value.to_bytes(16, 'little'), 128)
    else:
        key, iv = bytes.fromhex(inp['key']), bytes.fromhex(inp['iv'])
        algorithm = {'SNOW5G': 4, 'AES256': 5, 'ZUC256': 6}[suite]
        actual = Bits(nea_nia.keystream(algorithm, key, iv, exp['bit_length'] // 8), exp['bit_length'])
        if suite != 'AES256':
            state = snow5g.Snow5G(key, iv) if algorithm == 4 else zuc256.Zuc256(key, iv)
            wanted = {s['clock']: s['state'] for s in exp['states']}
            if len(wanted) != len(exp['states']) or not wanted:
                raise VectorError('Missing or duplicate implementation state inventory.')
            for clock in range(max(wanted) + 1):
                if clock in wanted:
                    snapshot = state.snapshot()
                    states.append(dict(clock=clock, expected=wanted[clock], actual=snapshot,
                                       status='PASS' if snapshot == wanted[clock] else 'FAIL'))
                if algorithm == 4:
                    z = state.clock()
                    state.a[8:] = [a ^ int.from_bytes(z[i * 2:i * 2 + 2], 'little')
                                   for i, a in enumerate(state.a[8:])]
                    if clock in (14, 15):
                        half = key[:16] if clock == 14 else key[16:]
                        state.r1 = bytes(a ^ b for a, b in zip(state.r1, half))
                else:
                    state.clock(initializing=clock < 48)
    return actual, states


def run(suites=None, source=None):
    from .validation import data_dir, identity
    source = Path(source) if source else data_dir() / '256'
    try:
        manifest, inputs, expected = [json.loads((source / f'{name}.json').read_text())
                                      for name in ('manifest', 'inputs', 'expected')]
    except (OSError, ValueError) as e:
        raise VectorError(f'256-bit official vector files are unavailable: {e}') from e
    if set(manifest['suites']) != set(REQUIRED) or manifest['required_total'] != 99:
        raise VectorError('256-bit manifest must declare the fixed 12 suites and 99 required cases.')
    chosen = list(suites) if suites else list(REQUIRED)
    if len(set(chosen)) != len(chosen) or any(s not in REQUIRED for s in chosen):
        raise VectorError('Unknown or duplicate 256-bit suite selection.')
    report = dict(category='official_256', environment=identity(), suites={}, cases=[], actual={})
    report['dataset_sha256'] = {name: hashlib.sha256((source / f'{name}.json').read_bytes()).hexdigest()
                                for name in ('manifest', 'inputs', 'expected')}
    for suite in chosen:
        entry = manifest['suites'][suite]
        count = REQUIRED[suite]
        records = entry['cases']
        ids = {f'{suite}-{n:03}' for n in range(1, count + 1)}
        if entry['required'] != count or len(records) != count or {r['id'] for r in records} != ids:
            raise VectorError(f'{suite}: required case inventory changed or contains duplicates.')
        counts = Counter({s: 0 for s in ('PASS', 'FAIL', 'ERROR', 'SKIP', 'BLOCKED')})
        for record in records:
            case = record['id']
            row = dict(id=case, source=record)
            try:
                inp, exp = inputs[case], expected[case]
                reference = Bits(bytes.fromhex(exp['buffer_hex']), exp['bit_length'])
                actual, states = calculate(case, inp, exp)
                row.update(expected=reference.to_dict(), actual=actual.to_dict(), states=states,
                           status='PASS' if actual == reference and all(s['status'] == 'PASS' for s in states) else 'FAIL')
                report['actual'][case] = actual.to_dict()
            except KeyError as e:
                row.update(status='BLOCKED', error=f'Missing input/expected field: {e}')
            except Exception as e:
                row.update(status='ERROR', error=f'{type(e).__name__}: {e}')
            counts[row['status']] += 1
            report['cases'].append(row)
        report['suites'][suite] = dict(required=count, **counts, match_rate=counts['PASS'] / count)
    report['required'] = sum(REQUIRED[s] for s in chosen)
    report['passed'] = sum(s['PASS'] for s in report['suites'].values())
    report['all_passed'] = report['passed'] == report['required'] and report['required'] > 0
    return report
