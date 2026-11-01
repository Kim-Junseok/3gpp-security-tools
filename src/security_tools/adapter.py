"""GUI-independent input conversion, shared by widget tests."""

from .bits import Bits
from .core import transmit, receive
from .errors import SecurityToolsError


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
        if value.length != 128:
            raise SecurityToolsError("Each non-Null key must contain exactly 128 bits.")
        return value.buffer

    cip = fields["ciphering"] if fields["cipher_enabled"] else None
    itg = fields["integrity"] if fields["integrity_enabled"] else None
    args = dict(ciphering=cip, integrity=itg, enc_key=key("enc_key", "enc_format", cip),
                int_key=key("int_key", "int_format", itg), count=number("count", 16),
                bearer=number("bearer", 10), direction=fields["direction"])
    data = Bits.parse(fields["data"], fields["data_format"])
    if receiving:
        if itg is not None and cip is None:
            args["received_mac"] = Bits.parse(fields["received_mac"], fields["mac_format"])
        return receive(data, **args)
    return transmit(data, **args)
