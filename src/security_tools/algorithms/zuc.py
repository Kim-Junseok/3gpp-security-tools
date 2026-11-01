"""ZUC v1.6 with EEA3/EIA3 v1.8 parameter and MAC construction."""

from .zuc_tables import S0, S1, D
from ..bits import Bits
from ..errors import SecurityToolsError

MASK = (1 << 32) - 1
MODULUS = (1 << 31) - 1


def _rotate(x, shift):
    return ((x << shift) | (x >> (32 - shift))) & MASK


def _linear(x, shifts):
    out = x
    for n in shifts:
        out ^= _rotate(x, n)
    return out


def _substitute(x):
    return int.from_bytes(bytes([S0[x >> 24], S1[(x >> 16) & 255], S0[(x >> 8) & 255], S1[x & 255]]), "big")


def keystream(key, iv, nwords):
    s = [(key[i] << 23) | (D[i] << 8) | iv[i] for i in range(16)]
    r1 = r2 = 0

    def reorganize():
        return (((s[15] & 0x7fff8000) << 1) | (s[14] & 0xffff),
                ((s[11] & 0xffff) << 16) | (s[9] >> 15),
                ((s[7] & 0xffff) << 16) | (s[5] >> 15),
                ((s[2] & 0xffff) << 16) | (s[0] >> 15))

    def nonlinear(x0, x1, x2):
        nonlocal r1, r2
        w = ((x0 ^ r1) + r2) & MASK
        w1, w2 = (r1 + x1) & MASK, r2 ^ x2
        u, v = ((w1 << 16) | (w2 >> 16)) & MASK, ((w2 << 16) | (w1 >> 16)) & MASK
        r1 = _substitute(_linear(u, (2, 10, 18, 24)))
        r2 = _substitute(_linear(v, (8, 14, 22, 30)))
        return w

    def clock(u=0):
        value = (s[0] + (s[0] << 8) + (s[4] << 20) + (s[10] << 21) + (s[13] << 17) + (s[15] << 15) + u) % MODULUS
        s[:] = s[1:] + [value or MODULUS]

    for _ in range(32):
        x = reorganize()
        clock(nonlinear(*x[:3]) >> 1)
    x = reorganize()
    nonlinear(*x[:3])
    clock()
    result = []
    for _ in range(nwords):
        x = reorganize()
        result.append(nonlinear(*x[:3]) ^ x[3])
        clock()
    return result


def cipher(key, count, bearer, direction, data):
    if data.length > 2**32:
        raise SecurityToolsError("ZUC ciphering accepts at most 2^32 message bits.")
    half = count.to_bytes(4, "big") + bytes([(bearer << 3) | (direction << 2)]) + bytes(3)
    words = keystream(key, half * 2, (data.length + 31) // 32)
    return data.xor(Bits(b"".join(w.to_bytes(4, "big") for w in words), data.length))


def mac(key, count, bearer, direction, data):
    if not 1 <= data.length <= 2**32:
        raise SecurityToolsError("ZUC integrity requires 1..2^32 message bits.")
    half = count.to_bytes(4, "big") + bytes([bearer << 3]) + bytes(3)
    iv = bytearray(half * 2)
    iv[8] ^= direction << 7
    iv[14] ^= direction << 7
    words = keystream(key, iv, (data.length + 31) // 32 + 2)

    def word(position):
        index, shift = divmod(position, 32)
        return words[index] if shift == 0 else ((words[index] << shift) | (words[index + 1] >> (32 - shift))) & MASK

    value, length = data.integer, data.length
    tag = 0
    for i in range(length):
        if (value >> (length - 1 - i)) & 1:
            tag ^= word(i)
    tag ^= word(length)
    tag ^= words[-1]
    return Bits.from_int(tag, 32)
