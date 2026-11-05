"""GUI-independent input conversion, shared by widget tests."""

import re

from .bits import Bits
from .core import transmit, receive, key_bits
from .errors import SecurityToolsError


COUNT_FORMATS = ("Decimal", "Hex", "Bit")


def parse_count(text, fmt="Decimal"):
    """Read an unsigned 32-bit COUNT independently of byte-oriented data input."""
    patterns = {"Decimal": (r"[0-9]+", 10), "Hex": (r"[0-9a-fA-F]+", 16), "Bit": (r"[01]+", 2)}
    if fmt not in patterns:
        raise SecurityToolsError("COUNT format must be Decimal, Hex, or Bit.")
    value = text.strip() if fmt == "Decimal" else "".join(text.split())
    pattern, radix = patterns[fmt]
    if not re.fullmatch(pattern, value):
        raise SecurityToolsError(f"COUNT must contain valid {fmt} digits.")
    # Reject overflow without converting an arbitrarily long decimal string.
    significant = value.lstrip("0") or "0"
    if len(significant) > {10: 10, 16: 8, 2: 32}[radix]:
        raise SecurityToolsError("COUNT must be in 0..4294967295 (32-bit unsigned).")
    count = int(significant, radix)
    if count > 0xFFFFFFFF:
        raise SecurityToolsError("COUNT must be in 0..4294967295 (32-bit unsigned).")
    return count


def format_data(data, fmt="Hex"):
    """Format GUI text while preserving the Core's serialized representation."""
    value = data.format(fmt)
    return " ".join(value[n:n + 2] for n in range(0, len(value), 2)).upper() if fmt == "Hex" else value


def execute(fields, receiving=False):
    def number(name, radix):
        try:
            return int(fields[name].strip(), radix)
        except (ValueError, KeyError) as e:
            raise SecurityToolsError(f"{name.upper()} must be {'hexadecimal' if radix == 16 else 'decimal'}.") from e

    def key(name, fmt, algorithm):
        if algorithm in (None, 0):
            return b""
        value = Bits.parse(fields[name], fields[fmt])
        required = key_bits(algorithm)
        if value.length != required:
            raise SecurityToolsError(f"Algorithm {algorithm} requires an exact {required}-bit key.")
        return value.buffer

    cip = fields["ciphering"] if fields["cipher_enabled"] else None
    itg = fields["integrity"] if fields["integrity_enabled"] else None
    needs_params = cip not in (None, 0) or itg not in (None, 0)
    args = dict(ciphering=cip, integrity=itg, enc_key=key("enc_key", "enc_format", cip),
                int_key=key("int_key", "int_format", itg),
                count=parse_count(fields["count"], fields.get("count_format", "Decimal")) if needs_params else 0,
                bearer=number("bearer", 10) if needs_params else 0, direction=fields["direction"] if needs_params else 0)
    newer = any(a in (4, 5, 6) for a in (cip, itg))
    if newer:
        extra_iv = Bits.parse(fields.get("extra_iv", "00" * 6), fields.get("extra_format", "Hex"))
        if extra_iv.length != 48:
            raise SecurityToolsError("EXTRA_IV must contain exactly 48 bits.")
        args["extra_iv"] = extra_iv.buffer
    if itg in (4, 5, 6):
        args["mac_bytes"] = number("mac_bytes", 10) if "mac_bytes" in fields else 4
    data = Bits.parse(fields["data"], fields["data_format"])
    if receiving:
        return receive(data, **args)
    return transmit(data, **args)
