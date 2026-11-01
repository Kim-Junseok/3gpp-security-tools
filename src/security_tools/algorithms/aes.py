"""AES-128, CTR and bit-oriented CMAC (TS 33.401 Annex B)."""

from functools import lru_cache
from ..bits import Bits


def _mul(a, b):
    out = 0
    for _ in range(8):
        if b & 1:
            out ^= a
        a = ((a << 1) ^ (0x11b if a & 0x80 else 0)) & 255
        b >>= 1
    return out


def _sbox(x):
    inv = 0 if x == 0 else 1
    if x:
        # a**254 in GF(2**8), computed once at module import.
        for _ in range(254):
            inv = _mul(inv, x)
    return inv ^ ((inv << 1 | inv >> 7) & 255) ^ ((inv << 2 | inv >> 6) & 255) ^ ((inv << 3 | inv >> 5) & 255) ^ ((inv << 4 | inv >> 4) & 255) ^ 0x63


SBOX = tuple(_sbox(x) for x in range(256))


@lru_cache(maxsize=32)
def _round_keys(key):
    schedule = list(key)
    rc = 1
    while len(schedule) < 176:
        word = schedule[-4:]
        if len(schedule) % 16 == 0:
            word = [SBOX[x] for x in word[1:] + word[:1]]
            word[0] ^= rc
            rc = _mul(rc, 2)
        for x in word:
            schedule.append(schedule[-16] ^ x)
    return tuple(tuple(schedule[n:n + 16]) for n in range(0, 176, 16))


def encrypt_block(key, block):
    if len(key) != 16 or len(block) != 16:
        raise ValueError("AES-128 requires a 16-byte key and block.")
    keys = _round_keys(key)
    s = [a ^ b for a, b in zip(block, keys[0])]
    for round_number in range(1, 11):
        s = [SBOX[x] for x in s]
        s = [s[4 * ((c + r) % 4) + r] for c in range(4) for r in range(4)]
        if round_number < 10:
            for c in range(4):
                j = 4 * c
                a, b, d, e = s[j:j + 4]
                s[j:j + 4] = [_mul(a, 2) ^ _mul(b, 3) ^ d ^ e,
                              a ^ _mul(b, 2) ^ _mul(d, 3) ^ e,
                              a ^ b ^ _mul(d, 2) ^ _mul(e, 3),
                              _mul(a, 3) ^ b ^ d ^ _mul(e, 2)]
        s = [a ^ b for a, b in zip(s, keys[round_number])]
    return bytes(s)


def cipher(key, count, bearer, direction, data):
    prefix = count.to_bytes(4, "big") + bytes([(bearer << 3) | (direction << 2)]) + bytes(3)
    stream = b"".join(encrypt_block(key, prefix + n.to_bytes(8, "big"))
                      for n in range((data.length + 127) // 128))
    return data.xor(Bits(stream, data.length))


def cmac(key, message):
    mask = (1 << 128) - 1

    def double(x):
        return ((x << 1) & mask) ^ (0x87 if x >> 127 else 0)

    k1 = double(int.from_bytes(encrypt_block(key, bytes(16)), "big"))
    k2 = double(k1)
    n = max(1, (message.length + 127) // 128)
    complete = message.length != 0 and message.length % 128 == 0
    value = message.integer
    state = 0
    for i in range(n - 1):
        chunk = (value >> (message.length - 128 * (i + 1))) & mask
        state = int.from_bytes(encrypt_block(key, (state ^ chunk).to_bytes(16, "big")), "big")
    tail_length = message.length - 128 * (n - 1)
    tail = value & ((1 << tail_length) - 1)
    last = tail ^ k1 if complete else ((tail << (128 - tail_length)) | (1 << (127 - tail_length))) ^ k2
    return encrypt_block(key, (state ^ last).to_bytes(16, "big"))


def mac(key, count, bearer, direction, data):
    header = count.to_bytes(4, "big") + bytes([(bearer << 3) | (direction << 2)]) + bytes(3)
    return Bits(cmac(key, Bits(header, 64).concat(data))[:4], 32)
