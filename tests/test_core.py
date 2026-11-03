import itertools
import json
from pathlib import Path
import unittest

from security_tools.bits import Bits, from_result
from security_tools.core import cipher, mac, verify, transmit, receive
from security_tools.errors import SecurityToolsError, UnsupportedAlgorithm, VectorError
from security_tools.adapter import execute, format_data, parse_count
from security_tools.validation import run

KEY = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
INT_KEY = bytes.fromhex("f0e0d0c0b0a090807060504030201000")
PARAMS = dict(count=0x12345678, bearer=17, direction=1)


class BitTests(unittest.TestCase):
    def test_leading_zero_whitespace(self):
        data = Bits.parse("00 01\t0a\n")
        self.assertEqual(data.format("Bit"), "000000000000000100001010")
        self.assertEqual(Bits.parse(data.format("Bit"), "Bit"), data)

    def test_reject_invalid_text(self):
        for text, fmt in [("0", "Hex"), ("0x00", "Hex"), ("gg", "Hex"), ("1012", "Bit"), ("0_1", "Bit"), ("00", "bad")]:
            with self.subTest(text=text, fmt=fmt), self.assertRaises(SecurityToolsError):
                Bits.parse(text, fmt)

    def test_buffer_length_and_unused_bits(self):
        self.assertEqual(Bits(bytes.fromhex("00ff"), 9).format("Bit"), "000000001")
        self.assertEqual(Bits(bytes.fromhex("ff"), 3).buffer, b"\xe0")
        for n in (-1, 9, True):
            with self.subTest(n=n), self.assertRaises(SecurityToolsError):
                Bits(b"\xff", n)

    def test_non_aligned_format(self):
        with self.assertRaises(SecurityToolsError):
            Bits.parse("00101", "Bit").format("Hex")

    def test_all_short_concatenations_and_splits(self):
        for a, b in itertools.product(range(10), repeat=2):
            x, y = "0" * a, ("101001011"[:b])
            left, right = Bits.parse(x, "Bit"), Bits.parse(y, "Bit")
            joined = left.concat(right)
            with self.subTest(a=a, b=b):
                self.assertEqual(joined.format("Bit"), x + y)
                self.assertEqual(joined.split(a), (left, right))


class CoreTests(unittest.TestCase):
    def test_range_checks(self):
        for name, value in [("count", -1), ("count", 2**32), ("count", True), ("bearer", 32), ("direction", 2)]:
            options = PARAMS | {name: value}
            with self.subTest(name=name, value=value), self.assertRaises(SecurityToolsError):
                cipher(2, KEY, data=Bits.parse("00"), **options)

    def test_key_checks_and_unsupported(self):
        for key in (b"", bytes(15), bytes(17), "0" * 16):
            with self.subTest(key_length=len(key)), self.assertRaises(SecurityToolsError):
                mac(2, key, data=Bits.parse("00"), **PARAMS)
        for number in (7, 8, 9, -1, True):
            with self.subTest(number=number), self.assertRaises(UnsupportedAlgorithm):
                cipher(number, KEY, data=Bits.parse("00"), **PARAMS)

    def test_null_definition(self):
        data = Bits.parse("000101001", "Bit")
        self.assertEqual(cipher(0, b"", data=data, **PARAMS), data)
        self.assertEqual(mac(0, b"", data=data, **PARAMS), Bits(bytes(4), 32))
        result = verify(0, b"", data=data, received_mac=Bits(bytes(4), 32), **PARAMS)
        self.assertTrue(result["matches"])
        self.assertFalse(result["authenticated"])
        self.assertEqual(result["authentication"], "unprotected")

    def test_all_combined_reference_and_roundtrip(self):
        # The reference concatenation uses strings, not Bits.concat or transmit.
        # The individual primitives are separately checked with official vectors.
        for c, i, text in itertools.product(range(4), range(4), ["0000000010100101", "00010100101"]):
            data = Bits.parse(text, "Bit")
            options = dict(ciphering=c, integrity=i, enc_key=KEY, int_key=INT_KEY, **PARAMS)
            tag = mac(i, INT_KEY, data=data, **PARAMS)
            ref_data = Bits.parse(text + tag.format("Bit"), "Bit")
            reference = cipher(c, KEY, data=ref_data, **PARAMS)
            with self.subTest(ciphering=c, integrity=i, length=len(text)):
                tx = transmit(data, **options)
                self.assertEqual(tx["data"], reference.to_dict())
                self.assertEqual(tx["cipher_bit_length"], data.length + 32)
                self.assertEqual(tx["mac_i"], tag.to_dict())
                rx = receive(reference, **options)
                self.assertEqual(rx["data"], data.to_dict())
                self.assertTrue(rx["matches"])
                self.assertEqual(rx["authenticated"], i != 0)
                self.assertEqual(rx["calculated_mac"], tag.to_dict())

    def test_data_and_mac_tampering(self):
        for c, i, text, area in itertools.product(range(4), range(1, 4), ["0000000010100101", "00010100101"], ["data", "mac"]):
            data = Bits.parse(text, "Bit")
            options = dict(ciphering=c, integrity=i, enc_key=KEY, int_key=INT_KEY, **PARAMS)
            payload = from_result(transmit(data, **options)["data"])
            position = 1 if area == "data" else data.length + 7
            altered = Bits.from_int(payload.integer ^ (1 << (payload.length - 1 - position)), payload.length)
            with self.subTest(ciphering=c, integrity=i, length=len(text), area=area):
                result = receive(altered, **options)
                self.assertFalse(result["matches"])
                self.assertFalse(result["authenticated"])
                self.assertEqual(result["authentication"], "failed")

    def test_short_combined_receive(self):
        for length in (0, 1, 7, 31):
            with self.subTest(length=length), self.assertRaises(SecurityToolsError):
                receive(Bits.from_int(0, length), ciphering=2, integrity=2, enc_key=KEY, int_key=INT_KEY)

    def test_disabled_differs_from_null(self):
        data = Bits.parse("0001")
        null = transmit(data, ciphering=0, integrity=0)
        disabled = transmit(data, ciphering=0)
        self.assertEqual(null["data"]["bit_length"], data.length + 32)
        self.assertEqual(disabled["data"]["bit_length"], data.length)
        with self.assertRaises(SecurityToolsError):
            transmit(data)

    def test_independent_cipher_and_integrity(self):
        data = Bits.parse("000011011", "Bit")
        for a in range(4):
            with self.subTest(algorithm=a):
                tx = transmit(data, ciphering=a, enc_key=KEY, **PARAMS)
                self.assertEqual(receive(from_result(tx["data"]), ciphering=a, enc_key=KEY, **PARAMS)["data"], data.to_dict())
                tag = mac(a, INT_KEY, data=data, **PARAMS)
                tx = transmit(data, integrity=a, int_key=INT_KEY, **PARAMS)
                self.assertEqual(tx["data"], data.to_dict())
                self.assertEqual(tx["mac_i"], tag.to_dict())
                self.assertTrue(receive(data, integrity=a, int_key=INT_KEY, received_mac=tag, **PARAMS)["matches"])

    def test_bad_mac_length(self):
        with self.assertRaises(SecurityToolsError):
            verify(2, KEY, data=Bits.parse("00"), received_mac=Bits.parse("00"), **PARAMS)

    def test_official_tail_bits_are_not_message_bits(self):
        for algorithm in range(1, 4):
            with self.subTest(algorithm=algorithm):
                a, b = Bits(b"\xa0", 3), Bits(b"\xbf", 3)
                self.assertEqual(mac(algorithm, KEY, data=a, **PARAMS), mac(algorithm, KEY, data=b, **PARAMS))


class MappingTests(unittest.TestCase):
    def test_cip1_official_key_iv_mapping(self):
        from security_tools.algorithms.snow import uea2_state_inputs
        # Key-word and IV table printed in SAGE Document 3 §4.3 p12.
        key = bytes.fromhex("2bd6459f82c5b300952c49104881ff48")
        words, iv = uea2_state_inputs(key, 0x72a4f20f, 0x0c, 1)
        self.assertEqual(words, [0x4881ff48, 0x952c4910, 0x82c5b300, 0x2bd6459f])
        self.assertEqual(iv, [0x64000000, 0x72a4f20f, 0x64000000, 0x72a4f20f])


class AdapterTests(unittest.TestCase):
    def fields(self):
        return dict(cipher_enabled=True, integrity_enabled=True, ciphering=2, integrity=2,
                    enc_key=KEY.hex(), int_key=INT_KEY.hex(), enc_format="Hex", int_format="Hex",
                    data="00010100101", data_format="Bit", count="12345678", count_format="Hex", bearer="17", direction=1,
                    received_mac="", mac_format="Hex")

    def test_same_as_direct_core(self):
        fields = self.fields()
        result = execute(fields)
        direct = transmit(Bits.parse(fields["data"], "Bit"), ciphering=2, integrity=2, enc_key=KEY, int_key=INT_KEY, **PARAMS)
        self.assertEqual(result, direct)
        received = fields | {"data": result["data"]["bits"]}
        self.assertEqual(execute(received, True)["data"]["bits"], fields["data"])

    def test_bit_key(self):
        fields = self.fields()
        bit_key = fields | {"enc_key": Bits(KEY, 128).format("Bit"), "enc_format": "Bit"}
        self.assertEqual(execute(fields), execute(bit_key))

    def test_invalid_number_and_key(self):
        for patch in [{"count": "xyz"}, {"bearer": "0x11"}, {"enc_key": "00"}]:
            with self.subTest(patch=patch), self.assertRaises(SecurityToolsError):
                execute(self.fields() | patch)

    def test_count_formats_preserve_parameters(self):
        reference = execute(self.fields())
        for fmt, value in [("Decimal", str(PARAMS["count"])), ("Hex", "12 34 56 78"),
                           ("Hex", "12345678"), ("Bit", "00010010 00110100 01010110 01111000")]:
            with self.subTest(fmt=fmt, value=value):
                self.assertEqual(execute(self.fields() | {"count": value, "count_format": fmt}), reference)
        default = self.fields() | {"count": str(PARAMS["count"])}
        del default["count_format"]
        self.assertEqual(execute(default), reference)

    def test_count_boundaries_and_invalid_formats(self):
        for fmt, maximum in [("Decimal", "4294967295"), ("Hex", "FFFFFFFF"), ("Bit", "1" * 32)]:
            with self.subTest(fmt=fmt):
                self.assertEqual(parse_count(maximum, fmt), 2**32 - 1)
                self.assertEqual(parse_count("0", fmt), 0)
                self.assertEqual(parse_count("0" * 100 + maximum, fmt), 2**32 - 1)
        invalid = [("4294967296", "Decimal"), ("100000000", "Hex"), ("1" + "0" * 32, "Bit"),
                   ("-1", "Decimal"), ("+1", "Decimal"), ("1_000", "Decimal"), ("1 0", "Decimal"),
                   ("", "Hex"), ("GG", "Hex"), ("102", "Bit"), ("1", "bad"),
                   ("9" * 5000, "Decimal")]
        for value, fmt in invalid:
            with self.subTest(fmt=fmt, value=value[:40]), self.assertRaises(SecurityToolsError):
                parse_count(value, fmt)

    def test_gui_hex_format_preserves_bytes_and_bits(self):
        data = Bits.parse("00 01 ab CD")
        self.assertEqual(format_data(data), "00 01 AB CD")
        self.assertEqual(Bits.parse(format_data(data)), data)
        self.assertEqual(format_data(data, "Bit"), "00000000000000011010101111001101")
        self.assertEqual(data.to_dict()["hex"], "0001abcd")
        self.assertEqual(format_data(Bits.parse("")), "")
        with self.assertRaises(SecurityToolsError):
            format_data(Bits.parse("00101", "Bit"))


class InventoryTests(unittest.TestCase):
    def test_missing_case_does_not_pass(self):
        import tempfile
        root = Path(__file__).resolve().parents[1] / "testdata"
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("manifest", "inputs", "expected"):
                obj = json.loads((root / f"{name}.json").read_text())
                if name == "inputs":
                    del obj["Cip2-001"]
                Path(tmp, f"{name}.json").write_text(json.dumps(obj))
            report = run(["Cip2"], source=tmp)
            self.assertEqual(report["required"], 6)
            self.assertEqual(report["suites"]["Cip2"]["BLOCKED"], 1)
            self.assertFalse(report["all_passed"])

    def test_changed_denominator_rejected(self):
        import tempfile
        root = Path(__file__).resolve().parents[1] / "testdata"
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("manifest", "inputs", "expected"):
                obj = json.loads((root / f"{name}.json").read_text())
                if name == "manifest":
                    obj["suites"]["Cip2"]["required"] = 0
                    obj["suites"]["Cip2"]["cases"] = []
                Path(tmp, f"{name}.json").write_text(json.dumps(obj))
            with self.assertRaises(VectorError):
                run(["Cip2"], source=tmp)


if __name__ == "__main__":
    unittest.main()
