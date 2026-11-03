import itertools
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from security_tools.adapter import execute
from security_tools.bits import Bits, from_result
from security_tools.core import cipher, mac, receive, transmit, verify
from security_tools.errors import SecurityToolsError, VectorError
from security_tools.validation256 import run

KEY = bytes(range(32))
IV = bytes.fromhex('112233445566')
PARAMS = dict(count=0xdeadbeef, bearer=31, direction=1)


def key(a):
    return KEY if a >= 4 else KEY[:16]


class NewAlgorithmTests(unittest.TestCase):
    def test_fixed_official_inventory_and_internal_states(self):
        r = run()
        self.assertEqual((r['required'], r['passed']), (99, 99))
        self.assertTrue(r['all_passed'])
        self.assertTrue(all(c['states'] for c in r['cases'] if c['id'].startswith(('SNOW5G-', 'ZUC256-'))))

    def test_mixed_families_reference_roundtrip_and_tampering(self):
        for c, i, text in itertools.product(range(7), range(7), ['0000000010100101', '00010100101']):
            for size in ([4, 16] if i >= 4 else [4]):
                data = Bits.parse(text, 'Bit')
                options = dict(ciphering=c, integrity=i, enc_key=key(c), int_key=key(i),
                               extra_iv=IV, mac_bytes=size, **PARAMS)
                tag = mac(i, key(i), data=data, extra_iv=IV if i >= 4 else bytes(6), mac_bytes=size, **PARAMS)
                # Assemble the reference independently of production concat/split.
                joined = Bits.parse(text + tag.format('Bit'), 'Bit')
                reference = cipher(c, key(c), data=joined, extra_iv=IV if c >= 4 else bytes(6), **PARAMS)
                with self.subTest(c=c, i=i, length=len(text), mac_bytes=size):
                    tx = transmit(data, **options)
                    self.assertEqual(tx['data'], reference.to_dict())
                    self.assertEqual(tx['cipher_bit_length'], len(text) + size * 8)
                    rx = receive(reference, **options)
                    self.assertEqual(rx['data'], data.to_dict())
                    self.assertTrue(rx['matches'])
                    self.assertEqual(rx['authenticated'], i != 0)
                    if i:
                        for position in (0, len(text), reference.length - 1):
                            bad = Bits.from_int(reference.integer ^ (1 << (reference.length - position - 1)), reference.length)
                            self.assertEqual(receive(bad, **options)['authentication'], 'failed')

    def test_all_mac_lengths_independent_verify_and_domain_separation(self):
        for a in (4, 5, 6):
            for size in range(4, 17):
                with self.subTest(a=a, size=size):
                    data = Bits.parse('00101', 'Bit')
                    options = dict(integrity=a, int_key=KEY, extra_iv=IV, mac_bytes=size, **PARAMS)
                    tx = transmit(data, **options)
                    tag = from_result(tx['mac_i'])
                    self.assertEqual(tag.length, size * 8)
                    self.assertEqual(tx['data'], data.to_dict())
                    self.assertEqual(receive(data, received_mac=tag, **options)['authentication'], 'passed')
                    wrong_iv = bytes([IV[0] ^ 1]) + IV[1:]
                    self.assertEqual(receive(data, received_mac=tag, **(options | dict(extra_iv=wrong_iv)))['authentication'], 'failed')
                    if size < 16:
                        longer = mac(a, KEY, data=data, extra_iv=IV, mac_bytes=size + 1, **PARAMS)
                        self.assertNotEqual(longer.buffer[:size], tag.buffer)

    def test_empty_input_and_masked_tail_bits(self):
        # Official conformance sets 1, 4 and 5 explicitly include zero-length inputs.
        for a, length in itertools.product((4, 5, 6), (0, 1, 7, 8, 127, 128, 129)):
            data = Bits(bytes([0xff]) * ((length + 7) // 8), length)
            clean = Bits(data.buffer, length)
            options = dict(ciphering=a, integrity=a, enc_key=KEY, int_key=KEY, extra_iv=IV, mac_bytes=16, **PARAMS)
            with self.subTest(a=a, length=length):
                tx = transmit(data, **options)
                self.assertEqual(receive(from_result(tx['data']), **options)['data'], clean.to_dict())
                self.assertEqual(mac(a, KEY, data=data, **PARAMS), mac(a, KEY, data=clean, **PARAMS))

    def test_invalid_key_extra_iv_mac_size_and_short_receive(self):
        data = Bits.parse('00')
        for a in (4, 5, 6):
            for bad_key in (bytes(16), bytes(31), bytes(33), '0' * 32):
                with self.subTest(a=a, key_length=len(bad_key)), self.assertRaises(SecurityToolsError):
                    cipher(a, bad_key, data=data, **PARAMS)
            for iv in (b'', bytes(5), bytes(7), '0' * 6):
                with self.subTest(a=a, iv_length=len(iv)), self.assertRaises(SecurityToolsError):
                    mac(a, KEY, data=data, extra_iv=iv, **PARAMS)
            for size in (0, 3, 17, True, 4.0):
                with self.subTest(a=a, size=size), self.assertRaises(SecurityToolsError):
                    mac(a, KEY, data=data, mac_bytes=size, **PARAMS)
            with self.assertRaises(SecurityToolsError):
                receive(Bits.from_int(0, 127), ciphering=a, integrity=a, enc_key=KEY, int_key=KEY, mac_bytes=16)
            with self.assertRaises(SecurityToolsError):
                verify(a, KEY, data=data, received_mac=Bits(bytes(4), 32), mac_bytes=16, **PARAMS)
        with self.assertRaises(SecurityToolsError):
            mac(2, KEY[:16], data=data, mac_bytes=16, **PARAMS)

    def test_adapter_hex_bit_extra_iv_and_variable_mac(self):
        fields = dict(cipher_enabled=True, integrity_enabled=True, ciphering=4, integrity=6,
                      enc_key=KEY.hex(), int_key=KEY.hex(), enc_format='Hex', int_format='Hex',
                      data='00010100101', data_format='Bit', count='4294967295', count_format='Decimal',
                      bearer='31', direction=1, extra_iv=IV.hex(), extra_format='Hex', mac_bytes='15')
        tx = execute(fields)
        bit_fields = fields | dict(enc_key=Bits(KEY, 256).format('Bit'), enc_format='Bit',
                                   extra_iv=Bits(IV, 48).format('Bit'), extra_format='Bit')
        self.assertEqual(execute(bit_fields), tx)
        self.assertEqual(execute(fields | dict(data=tx['data']['bits']), True)['data']['bits'], fields['data'])
        for change in (dict(enc_key='00'), dict(extra_iv='00'), dict(mac_bytes='17'), dict(mac_bytes='bad')):
            with self.subTest(change=change), self.assertRaises(SecurityToolsError):
                execute(fields | change)

    def test_missing_vectors_and_changed_denominator_cannot_pass(self):
        source = Path(__file__).resolve().parents[1] / 'testdata/256'
        for kind in ('missing_case', 'missing_suite', 'duplicate_case', 'missing_file'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                dest = Path(tmp) / '256'
                shutil.copytree(source, dest)
                if kind == 'missing_case':
                    p = dest / 'inputs.json'
                    obj = json.loads(p.read_text())
                    del obj['NEA4-001']
                    p.write_text(json.dumps(obj))
                    r = run(['NEA4'], dest)
                    self.assertEqual((r['required'], r['passed']), (12, 11))
                    self.assertFalse(r['all_passed'])
                else:
                    p = dest / 'manifest.json'
                    obj = json.loads(p.read_text())
                    if kind == 'missing_suite':
                        del obj['suites']['NEA4']
                    elif kind == 'duplicate_case':
                        obj['suites']['NEA4']['cases'][-1] = obj['suites']['NEA4']['cases'][0]
                    else:
                        (dest / 'expected.json').unlink()
                    p.write_text(json.dumps(obj))
                    with self.assertRaises(VectorError):
                        run(['NEA4'], dest)
