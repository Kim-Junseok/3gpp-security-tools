"""ZUC-256 with 128-bit IV and 48 initialization rounds (TS 35.246 v20.0.0).

The key/IV loading differs from older ZUC-256 proposals using a 184-bit IV.
"""

from .zuc import MASK, MODULUS, _linear, _substitute

D = (0x64, 0x43, 0x7b, 0x2a, 0x11, 0x05, 0x51, 0x42,
     0x1a, 0x31, 0x18, 0x66, 0x14, 0x2e, 0x01, 0x5c)


class Zuc256:
    def __init__(self, key, iv):
        if len(key) != 32 or len(iv) != 16:
            raise ValueError("ZUC-256 requires a 32-byte key and a 16-byte IV.")
        upper = key[16:23] + iv[:8] + key[23:24]
        lower = key[24:31] + iv[8:] + key[31:32]
        self.s = [(key[i] << 23) ^ (D[i] << 16) ^ (upper[i] << 8) ^ lower[i]
                  for i in range(16)]
        self.r1 = self.r2 = 0

    def snapshot(self):
        return dict(LFSR=self.s[:], FSM_R1=self.r1, FSM_R2=self.r2)

    def clock(self, initializing=False):
        s = self.s
        x0 = ((s[15] & 0x7fff8000) << 1) | (s[14] & 0xffff)
        x1 = ((s[11] & 0xffff) << 16) | (s[9] >> 15)
        x2 = ((s[7] & 0xffff) << 16) | (s[5] >> 15)
        x3 = ((s[2] & 0xffff) << 16) | (s[0] >> 15)
        w = ((x0 ^ self.r1) + self.r2) & MASK
        w1, w2 = (self.r1 + x1) & MASK, self.r2 ^ x2
        u = ((w1 << 16) | (w2 >> 16)) & MASK
        v = ((w2 << 16) | (w1 >> 16)) & MASK
        self.r1 = _substitute(_linear(u, (2, 10, 18, 24)))
        self.r2 = _substitute(_linear(v, (8, 14, 22, 30)))
        feedback = (s[0] + (s[0] << 8) + (s[4] << 20) + (s[10] << 21) +
                    (s[13] << 17) + (s[15] << 15) + (w >> 1 if initializing else 0)) % MODULUS
        self.s = s[1:] + [feedback or MODULUS]
        return w ^ x3

    def initialize(self):
        for _ in range(48):
            self.clock(initializing=True)
        self.clock()


def keystream(key, iv, size):
    state = Zuc256(key, iv)
    state.initialize()
    return b"".join(state.clock().to_bytes(4, "big") for _ in range((size + 3) // 4))[:size]
