"""SNOW 3G: SAGE Document 2 v1.1; UEA2/UIA2 Document 1 v2.1.

EEA1 uses the UEA2 mapping in TS 33.401 C.3.
EIA1 uses FRESH = BEARER << 27, per TS 33.401 Annex B.
"""

from functools import lru_cache
from .aes import SBOX
from .snow_tables import SQ
from ..bits import Bits
from ..errors import SecurityToolsError

MASK = 0xffffffff


def _xtime(v, polynomial):
    return ((v << 1) ^ (polynomial if v & 128 else 0)) & 255


def _power(v, n):
    for _ in range(n):
        v = _xtime(v, 0xa9)
    return v


@lru_cache(maxsize=512)
def _alpha(v, divide=False):
    powers = (16, 39, 6, 64) if divide else (23, 245, 48, 239)
    return int.from_bytes(bytes(_power(v, n) for n in powers), "big")


def _substitute(word, box, polynomial):
    a, b, c, d = [box[x] for x in word.to_bytes(4, "big")]
    x, y, z, t = [_xtime(v, polynomial) for v in (a, b, c, d)]
    return int.from_bytes(bytes([x ^ b ^ c ^ t ^ d,
                                 x ^ a ^ y ^ c ^ d,
                                 a ^ y ^ b ^ z ^ d,
                                 a ^ b ^ z ^ c ^ t]), "big")


def key_words(key):
    return [int.from_bytes(key[i:i + 4], "big") for i in (12, 8, 4, 0)]


def uea2_state_inputs(key, count, bearer, direction):
    flags = (bearer << 27) | (direction << 26)
    return key_words(key), [flags, count, flags, count]


def keystream(words, iv, nwords):
    k0, k1, k2, k3 = words
    v0, v1, v2, v3 = iv
    s = [k0 ^ MASK, k1 ^ MASK, k2 ^ MASK, k3 ^ MASK,
         k0, k1, k2, k3, k0 ^ MASK, k1 ^ MASK ^ v3,
         k2 ^ MASK ^ v2, k3 ^ MASK, k0 ^ v1, k1, k2, k3 ^ v0]
    r1 = r2 = r3 = 0

    def clock_fsm():
        nonlocal r1, r2, r3
        output = ((s[15] + r1) & MASK) ^ r2
        r1, r2, r3 = (r2 + (r3 ^ s[5])) & MASK, _substitute(r1, SBOX, 0x1b), _substitute(r2, SQ, 0x69)
        return output

    def clock_lfsr(feedback=0):
        v = ((s[0] << 8) & MASK) ^ _alpha(s[0] >> 24) ^ s[2] ^ (s[11] >> 8) ^ _alpha(s[11] & 255, True) ^ feedback
        s[:] = s[1:] + [v]

    for _ in range(32):
        clock_lfsr(clock_fsm())
    clock_fsm()
    clock_lfsr()
    output = []
    for _ in range(nwords):
        output.append(clock_fsm() ^ s[0])
        clock_lfsr()
    return output


def cipher(key, count, bearer, direction, data):
    words, iv = uea2_state_inputs(key, count, bearer, direction)
    stream = keystream(words, iv, (data.length + 31) // 32)
    return data.xor(Bits(b"".join(w.to_bytes(4, "big") for w in stream), data.length))


def _multiply64(value, factor):
    result = 0
    for _ in range(64):
        if factor & 1:
            result ^= value
        value = ((value << 1) & ((1 << 64) - 1)) ^ (0x1b if value >> 63 else 0)
        factor >>= 1
    return result


def mac(key, count, bearer, direction, data):
    if not 1 <= data.length <= 2**32:
        raise SecurityToolsError("SNOW 3G integrity requires 1..2^32 message bits.")
    fresh = bearer << 27
    iv = [fresh ^ (direction << 15), count ^ (direction << 31), fresh, count]
    z = keystream(key_words(key), iv, 5)
    p, q = (z[0] << 32) | z[1], (z[2] << 32) | z[3]
    value, length = data.integer, data.length
    state = 0
    for offset in range(0, length, 64):
        size = min(64, length - offset)
        chunk = ((value >> (length - offset - size)) & ((1 << size) - 1)) << (64 - size)
        state = _multiply64(state ^ chunk, p)
    state = _multiply64(state ^ length, q)
    return Bits.from_int((state >> 32) ^ z[4], 32)
