"""Header encodings from TS 36.323/38.323 layout figures, not algorithm vectors."""

import unittest

from security_tools.adapter import execute, pdcp_header_from_fields
from security_tools.core import transmit
from security_tools.bits import Bits
from security_tools.errors import SecurityToolsError
from security_tools.pdcp import generate_header, SN_LENGTHS


class HeaderGenerationTests(unittest.TestCase):
    def test_fixed_layout_encodings(self):
        # Explicit expected bytes independently transcribed from the specified
        # header field positions; all reserved bits are zero.
        cases = [
            ("LTE SRB", 5, 0, "00"), ("LTE SRB", 5, 0x12345, "05"),
            ("LTE SRB", 5, 0xffffffff, "1f"),
            ("LTE DRB", 7, 0, "80"), ("LTE DRB", 7, 0x12345, "c5"),
            ("LTE DRB", 7, 0xffffffff, "ff"),
            ("LTE DRB", 12, 0x12345, "8345"), ("LTE DRB", 12, 0xffffffff, "8fff"),
            ("LTE DRB", 15, 0x12345, "a345"), ("LTE DRB", 15, 0xffffffff, "ffff"),
            ("LTE DRB", 18, 0x12345, "812345"), ("LTE DRB", 18, 0xffffffff, "83ffff"),
            ("NR DRB", 12, 0x12345, "8345"), ("NR DRB", 18, 0x12345, "812345"),
            ("NR DRB", 18, 0xffffffff, "83ffff"),
            ("NR SRB", 12, 0x12345, "0345"), ("NR SRB", 12, 0xffffffff, "0fff"),
        ]
        for kind, bits, count, expected in cases:
            with self.subTest(kind=kind, bits=bits, count=count):
                self.assertEqual(generate_header(count, bits, kind).hex(), expected)

    def test_hfn_is_not_encoded_and_sn_wraps(self):
        for kind, lengths in SN_LENGTHS.items():
            for bits in lengths:
                extras = dict(slrb_prefix=bytes.fromhex('401234')) if kind == 'LTE SLRB' else {}
                with self.subTest(kind=kind, bits=bits):
                    base = generate_header(0, bits, kind, **extras)
                    self.assertEqual(generate_header(1 << bits, bits, kind, **extras), base)
                    self.assertEqual(generate_header((7 << bits) | 3, bits, kind, **extras), generate_header(3, bits, kind, **extras))

    def test_lte_direction_specific_fields(self):
        self.assertEqual(generate_header(0x123, 12, 'LTE DRB', direction=0, ailc=1).hex(), 'c123')
        self.assertEqual(generate_header(0x12345, 18, 'LTE DRB', direction=1, poll=1).hex(), 'c12345')
        for patch in (dict(direction=0, poll=1), dict(direction=1, ailc=1)):
            with self.subTest(patch=patch), self.assertRaises(SecurityToolsError):
                generate_header(0x123, 12 if 'ailc' in patch else 18, 'LTE DRB', **patch)
        with self.assertRaises(SecurityToolsError):
            generate_header(0x123, 12, 'NR DRB', ailc=1)

    def test_slrb_needs_its_actual_prefix(self):
        self.assertEqual(generate_header(0x12345, 16, 'LTE SLRB', slrb_prefix=bytes.fromhex('401234')).hex(), '4012342345')
        for prefix in (b'', bytes(2), bytes(4), '401234'):
            with self.subTest(prefix=prefix), self.assertRaises(SecurityToolsError):
                generate_header(0, 16, 'LTE SLRB', slrb_prefix=prefix)

    def test_reject_control_pdu_and_invalid_inputs(self):
        for kind in ('LTE DRB', 'NR DRB'):
            with self.subTest(kind=kind), self.assertRaises(SecurityToolsError):
                generate_header(0, 12, kind, dc=0)
        for count in (-1, 2**32, True, '1'):
            with self.subTest(count=count), self.assertRaises(SecurityToolsError):
                generate_header(count)
        for kind, bits in (('LTE SRB', 12), ('NR SRB', 5), ('LTE DRB', 16), ('NR DRB', 7), ('unknown', 12)):
            with self.subTest(kind=kind, bits=bits), self.assertRaises(SecurityToolsError):
                generate_header(0, bits, kind)


class AutomaticAdapterTests(unittest.TestCase):
    def fields(self):
        return dict(mode='PDCP', pdcp_source='Automatic', pdcp_pdu_type='LTE DRB', pdcp_sn_bits='15', pdcp_dc='1',
                    pdcp_header='FF FF', pdcp_generated_header='FF FF', sdap_present=True, sdap_header='09',
                    cipher_enabled=True, integrity_enabled=True, ciphering=2, integrity=2,
                    enc_key=bytes(range(16)).hex(), int_key=bytes(range(16)).hex(), enc_format='Hex', int_format='Hex',
                    count='74565', count_format='Decimal', bearer='1', direction=0, data='000102', data_format='Hex')

    def test_formats_and_execution_use_count_not_cached_hex(self):
        fields = self.fields()
        reference = transmit(Bits.parse('000102'), mode='PDCP', ciphering=2, integrity=2,
                             enc_key=bytes(range(16)), int_key=bytes(range(16)), count=0x12345, bearer=1, direction=0,
                             pdcp_header=bytes.fromhex('a345'), sdap_header=b'\x09')
        for fmt, text in (('Decimal', '74565'), ('Hex', '00 01 23 45'), ('Bit', '00000000000000010010001101000101')):
            with self.subTest(fmt=fmt):
                f = fields | dict(count=text, count_format=fmt)
                self.assertEqual(pdcp_header_from_fields(f), bytes.fromhex('a345'))
                self.assertEqual(execute(f), reference)
                self.assertEqual(execute(f | dict(data=reference['data']['hex']), True)['authentication'], 'passed')

    def test_count_change_and_invalid_count_do_not_reuse_stale_header(self):
        fields = self.fields()
        self.assertEqual(pdcp_header_from_fields(fields | dict(count='74566')), bytes.fromhex('a346'))
        for count in ('', 'xyz', '-1', '4294967296'):
            with self.subTest(count=count), self.assertRaises(SecurityToolsError):
                execute(fields | dict(count=count))

    def test_manual_and_inactive_flag_values_preserved(self):
        f = self.fields()
        self.assertEqual(pdcp_header_from_fields(f | dict(pdcp_source='Manual Hex')), b'\xff\xff')
        # LTE flags and SLRB prefix do not apply to NR and must not affect its bytes.
        self.assertEqual(pdcp_header_from_fields(f | dict(pdcp_pdu_type='NR DRB', pdcp_sn_bits='12', pdcp_poll=True,
                                                         pdcp_ailc=True, pdcp_slrb_prefix='bad')), bytes.fromhex('8345'))
        with self.assertRaises(SecurityToolsError):
            pdcp_header_from_fields(f | dict(pdcp_source='bad'))
