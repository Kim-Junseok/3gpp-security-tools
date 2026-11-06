"""Protection-boundary tests, separate from official algorithm conformance.

PDCP framing references assemble bit strings independently of transmit/receive.
Official messages are also segmented to check input reassembly against fixed MACs;
those artificial segments are not claimed to be official PDCP packet vectors.
"""

import itertools
import json
from pathlib import Path
import unittest

from security_tools.adapter import execute, format_length
from security_tools.bits import Bits, from_result
from security_tools.core import cipher, mac, transmit, receive
from security_tools.errors import SecurityToolsError

ROOT = Path(__file__).resolve().parents[1]
HEADER = bytes.fromhex('8123')
SDAP = bytes.fromhex('09')
RADIO = dict(count=0x123, bearer=1, direction=0)


def key(a):
    return bytes(range(16 if a < 4 else 32))


class PdcpTests(unittest.TestCase):
    def test_header_reassembly_matches_official_mac_expectations(self):
        for folder in (ROOT / 'testdata', ROOT / 'testdata/256'):
            inputs = json.loads((folder / 'inputs.json').read_text())
            expected = json.loads((folder / 'expected.json').read_text())
            for case, inp in inputs.items():
                if not case.startswith(('Itg', 'NIA')) or inp['bit_length'] < 24:
                    continue
                with self.subTest(case=case):
                    message = Bits(bytes.fromhex(inp['buffer_hex']), inp['bit_length'])
                    text = message.format('Bit')
                    pdcp = bytes.fromhex(inp['buffer_hex'])[:2]
                    sdap = bytes.fromhex(inp['buffer_hex'])[2:3]
                    payload = Bits.parse(text[24:], 'Bit')
                    options = dict(mode='PDCP', integrity=int(case.split('-')[0][-1]), int_key=bytes.fromhex(inp['key']),
                                   count=inp['count'], bearer=inp['bearer'], direction=inp['direction'],
                                   pdcp_header=pdcp, sdap_header=sdap,
                                   extra_iv=bytes.fromhex(inp.get('extra_iv', '00' * 6)), mac_bytes=inp.get('mac_bytes', 4))
                    tx = transmit(payload, **options)
                    exp = expected[case]
                    reference = Bits(bytes.fromhex(exp['buffer_hex']), exp['bit_length'])
                    self.assertEqual(from_result(tx['mac_i']), reference)
                    self.assertEqual(tx['integrity_input_bit_length'], inp['bit_length'])
                    packet = Bits.parse(payload.format('Bit') + reference.format('Bit'), 'Bit')
                    rx = receive(packet, **options)
                    self.assertEqual(rx['authentication'], 'passed')
                    self.assertEqual(rx['data'], payload.to_dict())

    def test_pdcp_cipher_boundary_all_families_and_mac_lengths(self):
        for c, i, sdap, text in itertools.product(range(7), range(7), (b'', SDAP), ('', '0010101', '000000001010010100000001')):
            for size in ([4, 16] if i >= 4 else [4]):
                with self.subTest(ciphering=c, integrity=i, sdap=sdap.hex(), length=len(text), mac_bytes=size):
                    payload = Bits.parse(text, 'Bit')
                    # Only the MAC reference includes clear headers.
                    prefix = Bits(HEADER + sdap, (len(HEADER) + len(sdap)) * 8).format('Bit')
                    message = Bits.parse(prefix + text, 'Bit')
                    tag = mac(i, key(i), data=message, mac_bytes=size, **RADIO)
                    cipher_input = Bits.parse(text + tag.format('Bit'), 'Bit')
                    reference = cipher(c, key(c), data=cipher_input, **RADIO)
                    options = dict(mode='PDCP', pdcp_header=HEADER, sdap_header=sdap, ciphering=c, integrity=i,
                                   enc_key=key(c), int_key=key(i), mac_bytes=size, **RADIO)
                    tx = transmit(payload, **options)
                    self.assertEqual(tx['data'], reference.to_dict())
                    self.assertEqual(tx['cipher_bit_length'], len(text) + size * 8)
                    self.assertEqual(tx['mac_i'], tag.to_dict())
                    self.assertEqual(tx['integrity_header_bit_length'], len(prefix))
                    rx = receive(reference, **options)
                    self.assertEqual(rx['data'], payload.to_dict())
                    self.assertEqual(rx['authentication'], 'passed' if i else 'unprotected')

    def test_header_and_payload_tampering_are_detected(self):
        for a, sdap in itertools.product(range(1, 7), (b'', SDAP)):
            for size in (range(4, 17) if a >= 4 else [4]):
                options = dict(mode='PDCP', pdcp_header=HEADER, sdap_header=sdap, ciphering=a, integrity=a,
                               enc_key=key(a), int_key=key(a), mac_bytes=size, **RADIO)
                payload = Bits.parse('000102')
                tx = transmit(payload, **options)
                encoded = from_result(tx['data'])
                for patch in (dict(pdcp_header=b'\x81\x24'), dict(sdap_header=b'\x0a')):
                    with self.subTest(a=a, size=size, patch=patch):
                        self.assertEqual(receive(encoded, **(options | patch))['authentication'], 'failed')
                for position in (0, encoded.length - 1):
                    bad = Bits.from_int(encoded.integer ^ (1 << position), encoded.length)
                    self.assertEqual(receive(bad, **options)['authentication'], 'failed')

    def test_pdcp_header_requirements_and_raw_compatibility(self):
        payload = Bits.parse('00')
        for fn in (transmit, receive):
            for i in range(7):
                with self.subTest(fn=fn.__name__, i=i), self.assertRaises(SecurityToolsError):
                    fn(payload, mode='PDCP', integrity=i, int_key=key(i))
            for patch in (dict(mode='wrong'), dict(mode='Raw', pdcp_header=HEADER),
                          dict(mode='PDCP', pdcp_header='8123'), dict(mode='PDCP', pdcp_header=HEADER, sdap_header=b'\0\0')):
                with self.subTest(patch=patch), self.assertRaises(SecurityToolsError):
                    fn(payload, integrity=2, int_key=key(2), **patch)
        self.assertEqual(transmit(payload, ciphering=2, enc_key=key(2)),
                         transmit(payload, ciphering=2, enc_key=key(2), mode='PDCP'))
        options = dict(integrity=2, int_key=key(2), mode='PDCP', pdcp_header=HEADER, sdap_header=SDAP)
        tx = transmit(payload, **options)
        rx = receive(payload, received_mac=from_result(tx['mac_i']), **options)
        self.assertEqual(rx['data'], payload.to_dict())
        self.assertEqual(rx['authentication'], 'passed')
        self.assertEqual(tx['data'], payload.to_dict())


class HeaderAdapterTests(unittest.TestCase):
    def fields(self):
        return dict(mode='PDCP', cipher_enabled=True, integrity_enabled=True, ciphering=2, integrity=2,
                    enc_key=key(2).hex(), int_key=key(2).hex(), enc_format='Hex', int_format='Hex',
                    count='291', bearer='1', direction=0, data='000102', data_format='Hex',
                    pdcp_header='81 23', sdap_present=True, sdap_header='09')

    def test_adapter_roundtrip_and_presence_validation(self):
        f = self.fields()
        tx = execute(f)
        rx = execute(f | dict(data=tx['data']['hex']), receiving=True)
        self.assertEqual(rx['data']['hex'], f['data'])
        self.assertEqual(rx['authentication'], 'passed')
        for patch in (dict(pdcp_header=''), dict(pdcp_header='ABC'), dict(sdap_header=''),
                      dict(sdap_header='0000'), dict(sdap_header='XX')):
            with self.subTest(patch=patch), self.assertRaises(SecurityToolsError):
                execute(f | patch)
        # Disabled header inputs must not silently change Raw/cipher-only calculations.
        self.assertEqual(execute(f | dict(mode='Raw', pdcp_header='bad', sdap_header='bad')),
                         execute(f | dict(mode='Raw', pdcp_header='', sdap_header='', sdap_present=False)))
        self.assertEqual(execute(f | dict(integrity_enabled=False, pdcp_header='bad', sdap_header='bad')),
                         execute(f | dict(integrity_enabled=False, pdcp_header='', sdap_header='', sdap_present=False)))
        self.assertEqual(execute(f | dict(sdap_present=False, sdap_header='bad')),
                         execute(f | dict(sdap_present=False, sdap_header='')))

    def test_exact_bit_and_byte_lengths(self):
        for bits, expected in ((0, '0 bit (0 bytes)'), (8, '8 bit (1 byte)'), (128, '128 bit (16 bytes)'),
                               (7, '7 bit (0 bytes + 7 bits)'), (9, '9 bit (1 byte + 1 bit)'),
                               (43, '43 bit (5 bytes + 3 bits)')):
            self.assertEqual(format_length(bits), expected)
