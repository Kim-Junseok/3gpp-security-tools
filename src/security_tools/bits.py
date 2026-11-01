"""MSB-first buffers with an explicit valid bit length."""

from dataclasses import dataclass
import re

from .errors import SecurityToolsError


@dataclass(frozen=True)
class Bits:
    buffer: bytes
    length: int

    def __post_init__(self):
        if not isinstance(self.buffer, bytes):
            raise SecurityToolsError("Data buffer must be bytes.")
        if type(self.length) is not int or not 0 <= self.length <= len(self.buffer) * 8:
            raise SecurityToolsError("Valid bit length must fit the buffer.")
        size = (self.length + 7) // 8
        buf = self.buffer[:size]
        if self.length % 8:
            buf = buf[:-1] + bytes([buf[-1] & (255 << (8 - self.length % 8))])
        object.__setattr__(self, "buffer", buf)

    @classmethod
    def from_int(cls, value, length):
        if type(length) is not int or length < 0 or type(value) is not int or not 0 <= value < (1 << length):
            raise SecurityToolsError("Integer does not fit the bit length.")
        shift = (-length) % 8
        return cls((value << shift).to_bytes((length + 7) // 8, "big"), length)

    @classmethod
    def parse(cls, text, fmt="Hex"):
        compact = re.sub(r"\s+", "", text)
        if fmt == "Hex":
            if len(compact) % 2 or re.search(r"[^0-9a-fA-F]", compact):
                raise SecurityToolsError("Hex requires an even number of hexadecimal digits (whole bytes).")
            return cls(bytes.fromhex(compact), len(compact) * 4)
        if fmt == "Bit":
            if re.search(r"[^01]", compact):
                raise SecurityToolsError("Bit input accepts only 0, 1, and whitespace.")
            return cls.from_int(int(compact or "0", 2), len(compact))
        raise SecurityToolsError("Choose Hex or Bit.")

    @property
    def integer(self):
        return int.from_bytes(self.buffer, "big") >> ((-self.length) % 8)

    def format(self, fmt="Hex"):
        if fmt == "Hex":
            if self.length % 8:
                raise SecurityToolsError("Non-byte-aligned data must remain in Bit format; no padding is added.")
            return self.buffer.hex()
        if fmt == "Bit":
            return format(self.integer, f"0{self.length}b") if self.length else ""
        raise SecurityToolsError("Choose Hex or Bit.")

    def concat(self, other):
        return Bits.from_int((self.integer << other.length) | other.integer, self.length + other.length)

    def split(self, position):
        if type(position) is not int or not 0 <= position <= self.length:
            raise SecurityToolsError("Split position is outside the valid data.")
        tail = self.length - position
        return Bits.from_int(self.integer >> tail, position), Bits.from_int(self.integer & ((1 << tail) - 1), tail)

    def xor(self, other):
        if self.length != other.length:
            raise SecurityToolsError("XOR inputs must have equal valid lengths.")
        return Bits.from_int(self.integer ^ other.integer, self.length)

    def to_dict(self):
        return {"bit_length": self.length, "hex": self.buffer.hex() if self.length % 8 == 0 else None,
                "bits": self.format("Bit")}


def from_result(result):
    """Reconstitute an exact public Core result without using storage padding."""
    return Bits.parse(result["bits"], "Bit")
