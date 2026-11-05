"""NEA4/5/6 and NIA4/5/6, TS 35.240/243/246 v20.0.0 clauses 4, 5 and 7.

Only independent confidentiality and integrity functions are exposed. The
application's MAC-append/encrypt pipeline is separate from standardized NCA.
"""

from . import aes, snow5g, zuc256
from ..bits import Bits


def make_iv(count, bearer, direction, extra_iv=bytes(6), mac_bytes=0):
    # CF=LK=AI=0; AES sets AI only while generating H/Q/P.
    return bytes([mac_bytes << 3, (bearer << 1) | direction]) + extra_iv + count.to_bytes(4, "big") + bytes(4)


def keystream(algorithm, key, iv, size):
    if algorithm == 4:
        return snow5g.keystream(key, iv, size)
    if algorithm == 6:
        return zuc256.keystream(key, iv, size)
    return b"".join(aes.encrypt_block(key, iv[:12] + i.to_bytes(4, "big"))
                    for i in range((size + 15) // 16))[:size]


def pdot(a, b):
    """POLYVAL dot product on little-endian 128-bit integers, clause 5.2.3.3."""
    result = 0
    for i in range(128):
        if (a >> i) & 1:
            result ^= b
        result = (result >> 1) ^ ((0xe1 << 120) if result & 1 else 0)
    return result


def cipher(algorithm, key, count, bearer, direction, data, extra_iv):
    iv = make_iv(count, bearer, direction, extra_iv)
    stream = keystream(algorithm, key, iv, len(data.buffer))
    return data.xor(Bits(stream, data.length))


def mac(algorithm, key, count, bearer, direction, data, extra_iv, mac_bytes):
    iv = make_iv(count, bearer, direction, extra_iv, mac_bytes)
    if algorithm == 5:
        iv = bytes([iv[0] | 1]) + iv[1:]
    stream = keystream(algorithm, key, iv, 48)
    h, q, p = [int.from_bytes(stream[i:i + 16], "little") for i in (0, 16, 32)]
    accumulator = 0
    # Bits has already masked the unused low bits of the last byte.
    for i in range(0, len(data.buffer), 16):
        chunk = int.from_bytes(data.buffer[i:i + 16].ljust(16, b"\0"), "little")
        accumulator = pdot(accumulator ^ chunk, h)
    # NIA maps MESSAGE to AAD and uses an empty ciphertext.
    accumulator = pdot(accumulator ^ (data.length << 64), q) ^ p
    return Bits(accumulator.to_bytes(16, "little")[:mac_bytes], mac_bytes * 8)
