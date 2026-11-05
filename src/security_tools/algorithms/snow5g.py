"""SNOW 5G keystream generator, TS 35.240 v20.0.0 clause 6.

State words and FSM lanes use little-endian byte order. This is SNOW 5G,
not the legacy SNOW 3G generator.
"""

from .aes import SBOX, _mul


def _words(data):
    return [int.from_bytes(data[i:i + 2], "little") for i in range(0, len(data), 2)]


def _bytes(words):
    return b"".join(w.to_bytes(2, "little") for w in words)


def _aes_round(data):
    s = [SBOX[data[4 * ((c + r) % 4) + r]] for c in range(4) for r in range(4)]
    out = []
    for j in range(0, 16, 4):
        a, b, c, d = s[j:j + 4]
        out.extend((_mul(a, 2) ^ _mul(b, 3) ^ c ^ d,
                    a ^ _mul(b, 2) ^ _mul(c, 3) ^ d,
                    a ^ b ^ _mul(c, 2) ^ _mul(d, 3),
                    _mul(a, 3) ^ b ^ c ^ _mul(d, 2)))
    return bytes(out)


class Snow5G:
    def __init__(self, key, iv):
        if len(key) != 32 or len(iv) != 16:
            raise ValueError("SNOW 5G requires a 32-byte key and a 16-byte IV.")
        self.a = _words(iv + key[:16])
        self.b = _words(bytes(16) + key[16:])
        self.r1 = self.r2 = self.r3 = bytes(16)

    def snapshot(self):
        return dict(lfsrA=self.a[:], lfsrB=self.b[:],
                    R1=self.r1.hex(), R2=self.r2.hex(), R3=self.r3.hex())

    def clock(self):
        z = _bytes([((a + b) & 0xffff) ^ c for a, b, c in
                    zip(self.b[8:], _words(self.r1), _words(self.r2))])
        t = _bytes([((a ^ c) + b) & 0xffff for a, b, c in
                    zip(self.a[8:], _words(self.r2), _words(self.r3))])
        self.r3, self.r2 = _aes_round(self.r2), _aes_round(self.r1)
        self.r1 = bytes(t[i] for i in (0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15))
        a, b = self.a, self.b
        self.a = a[8:] + [(a[i + 7] ^ b[i] ^ (a[i] << 1) ^
                          (0x4a6d if a[i] >> 15 else 0)) & 0xffff for i in range(8)]
        self.b = b[8:] + [(b[i + 8] ^ a[i] ^ (b[i] << 1) ^
                          (0xcc87 if b[i] >> 15 else 0)) & 0xffff for i in range(8)]
        return z

    def initialize(self, key):
        for i in range(16):
            z = self.clock()
            self.a[8:] = [a ^ b for a, b in zip(self.a[8:], _words(z))]
            if i in (14, 15):
                half = key[:16] if i == 14 else key[16:]
                self.r1 = bytes(a ^ b for a, b in zip(self.r1, half))


def keystream(key, iv, size):
    state = Snow5G(key, iv)
    state.initialize(key)
    return b"".join(state.clock() for _ in range((size + 15) // 16))[:size]
