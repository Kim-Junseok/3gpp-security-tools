"""Import fixed Release 20 vectors directly from official DOCX XML.

Usage: python tools/import_256_vectors.py --specs local-specs
Download 35240-k00.zip through 35248-k00.zip from the 3GPP archive first.
No implementation or calculated output is imported by this script.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def document(path):
    with zipfile.ZipFile(path) as z:
        names = [n for n in z.namelist() if n.endswith('.docx')]
        assert len(names) == 1
        data = z.read(names[0])
    with zipfile.ZipFile(__import__('io').BytesIO(data)) as z:
        root = ET.fromstring(z.read('word/document.xml'))
    # Only w:t is visible document text; formatting and field instructions are ignored.
    paragraphs = [''.join(t.text or '' for t in p.findall('.//w:t', NS)).strip()
                  for p in root.findall('.//w:p', NS)]
    return '\n'.join(paragraphs), hashlib.sha256(data).hexdigest()


def arrays(text):
    return {name.strip(): ''.join(value.split()).lower()
            for name, value in re.findall(r'^([^\n{}]+?)\s*=\s*\{([^}]*)\}', text, re.M)}


def integers(text):
    return {name: int(value, 0) for name, value in
            re.findall(r'^(\w+)\s*=\s*(0x[0-9a-fA-F]+|[0-9]+)\s*$', text, re.M)}


def import_vectors(specs, output):
    manifest = dict(schema_version=1, required_total=99, scope='NEA/NIA and implementation primitives; NCA excluded',
                    documents={}, suites={})
    inputs, expected = {}, {}
    texts = {}
    for n in range(240, 249):
        path = specs / f'35{n}-k00.zip'
        text, doc_hash = document(path)
        assert 'V20.0.0' in text, path
        texts[n] = text
        manifest['documents'][f'TS 35.{n}'] = dict(
            version='20.0.0', url=f'https://www.3gpp.org/ftp/Specs/archive/35_series/35.{n}/{path.name}',
            archive_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), document_sha256=doc_hash)

    def add(suite, number, doc, section, inp, exp):
        entry = manifest['suites'].setdefault(suite, dict(required=0, cases=[]))
        case = f'{suite}-{number:03}'
        entry['required'] += 1
        entry['cases'].append(dict(id=case, document=f'TS 35.{doc}', section=section,
                                   source_test_set=number, **manifest['documents'][f'TS 35.{doc}']))
        inputs[case], expected[case] = inp, exp

    for algorithm, doc in [(4, 242), (5, 245), (6, 248)]:
        found = re.findall(r'=== (NEA|NIA|NCA)\d_256 TEST #(\d+) ===(.*?)(?====|\Z)', texts[doc], re.S)
        for kind in ('NEA', 'NIA'):
            cases = [(int(n), block) for k, n, block in found if k == kind]
            assert [n for n, _ in cases] == list(range(1, 13)), (doc, kind)
            for number, block in cases:
                a, v = arrays(block), integers(block)
                length = v['LENGTH']
                inp = dict(algorithm=algorithm, key=a['CK' if kind == 'NEA' else 'IK'],
                           count=v['COUNT_C' if kind == 'NEA' else 'COUNT_I'], bearer=v['BEARER'],
                           direction=v['DIRECTION'], extra_iv=a['EXTRA_IV'] or '00' * 6,
                           buffer_hex=a['IBS' if kind == 'NEA' else 'MESSAGE'], bit_length=length)
                if kind == 'NIA':
                    inp['mac_bytes'] = v['MAC_BYTES']
                exp = dict(buffer_hex=a['OBS' if kind == 'NEA' else 'MAC_I'],
                           bit_length=length if kind == 'NEA' else v['MAC_BYTES'] * 8)
                assert len(bytes.fromhex(inp['key'])) == 32
                assert len(bytes.fromhex(inp['buffer_hex'])) == (length + 7) // 8
                assert len(bytes.fromhex(exp['buffer_hex'])) == (exp['bit_length'] + 7) // 8
                add(f'{kind}{algorithm}', number, doc, '5.2' if kind == 'NEA' else '5.3', inp, exp)

    for doc, name in [(241, 'SNOW-5G'), (244, 'AES-256'), (247, 'ZUC-256')]:
        poly = re.findall(r'=== POLYVAL TEST #(\d+) ===(.*?)(?====|\Z)', texts[doc], re.S)
        assert len(poly) == 6
        for n, block in poly:
            a = arrays(block)
            add(f'POLYVAL{doc}', int(n), doc, '5.2', dict(a=a['A'], b=a['B']), dict(buffer_hex=a['A*B'], bit_length=128))
        cases = re.findall(r'=== ' + name + r' TEST #(\d+) ===(.*?)(?====|\Z)', texts[doc], re.S)
        assert len(cases) == 3
        for n, block in cases:
            a = arrays(block)
            inp = dict(key=a['KEY'], iv=a['IV'])
            if doc == 244:
                stream = ''.join(a[f'ks[ctr={i}]'] for i in range(4))
            elif doc == 241:
                stream = ''.join(a[f'ks_{i}'] for i in range(4))
            else:
                stream = a.get('Ks', a.get('ks'))
                assert stream is not None
            exp = dict(buffer_hex=stream, bit_length=len(stream) * 4, states=[])
            states = re.findall(r'State after (\(Key, IV\) loading|\d+ initialisation clocks)(.*?)(?=State after|Keystream mode:|\Z)', block, re.S)
            for title, state in states:
                clock = 0 if title.startswith('(') else int(title.split()[0])
                sa, sv = arrays(state), integers(state)
                if doc == 241:
                    snap = {k: [int(x, 16) for x in re.findall(r'[0-9a-fA-F]{4}', sa[k])]
                            for k in ('lfsrA', 'lfsrB')}
                    snap.update({k: sa[k] for k in ('R1', 'R2', 'R3')})
                elif doc == 247:
                    snap = dict(LFSR=[int(x, 16) for x in re.findall(r'[0-9a-fA-F]{8}', sa['LFSR'])],
                                FSM_R1=sv['FSM_R1'], FSM_R2=sv['FSM_R2'])
                else:
                    continue
                exp['states'].append(dict(clock=clock, state=snap))
            add({241: 'SNOW5G', 244: 'AES256', 247: 'ZUC256'}[doc], int(n), doc, '5.3', inp, exp)
    assert sum(s['required'] for s in manifest['suites'].values()) == 99
    output.mkdir(parents=True, exist_ok=True)
    for name, obj in [('manifest', manifest), ('inputs', inputs), ('expected', expected)]:
        (output / f'{name}.json').write_text(json.dumps(obj, indent=2) + '\n')
    print({s: v['required'] for s, v in manifest['suites'].items()})


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--specs', type=Path, default=ROOT / 'local-specs')
    p.add_argument('--output', type=Path, default=ROOT / 'testdata/256')
    args = p.parse_args()
    import_vectors(args.specs, args.output)
