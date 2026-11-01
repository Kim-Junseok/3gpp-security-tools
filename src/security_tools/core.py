"""Common calculation API used by GUI and official validation."""

from hmac import compare_digest
from .bits import Bits
from .errors import SecurityToolsError, UnsupportedAlgorithm


def _validate(algorithm, key, count, bearer, direction, data):
    if type(algorithm) is not int or algorithm not in range(4):
        raise UnsupportedAlgorithm("Only legacy algorithm numbers 0–3 are supported. 256-bit NEA/NIA are planned; NCA is excluded.")
    for name, value, maximum in [("COUNT", count, 2**32 - 1), ("BEARER", bearer, 31), ("DIRECTION", direction, 1)]:
        if type(value) is not int or not 0 <= value <= maximum:
            raise SecurityToolsError(f"{name} must be an integer in 0..{maximum}.")
    if not isinstance(data, Bits):
        raise SecurityToolsError("Core data must include its valid bit length (Bits).")
    if algorithm != 0 and (not isinstance(key, bytes) or len(key) != 16):
        raise SecurityToolsError("Non-Null legacy algorithms require an exact 128-bit key.")


def _module(algorithm):
    if algorithm == 2:
        from .algorithms import aes
        return aes
    if algorithm == 1:
        from .algorithms import snow
        return snow
    from .algorithms import zuc
    return zuc


def cipher(algorithm, key, count, bearer, direction, data):
    _validate(algorithm, key, count, bearer, direction, data)
    if algorithm == 0:
        return data
    return _module(algorithm).cipher(key, count, bearer, direction, data)


def mac(algorithm, key, count, bearer, direction, data):
    _validate(algorithm, key, count, bearer, direction, data)
    if algorithm == 0:
        return Bits(bytes(4), 32)
    return _module(algorithm).mac(key, count, bearer, direction, data)


def verify(algorithm, key, count, bearer, direction, data, received_mac):
    if not isinstance(received_mac, Bits) or received_mac.length != 32:
        raise SecurityToolsError("Received MAC-I must contain exactly 32 bits.")
    calculated = mac(algorithm, key, count, bearer, direction, data)
    matches = compare_digest(calculated.buffer, received_mac.buffer)
    return {"received_mac": received_mac.to_dict(), "calculated_mac": calculated.to_dict(),
            "matches": matches, "authenticated": algorithm != 0 and matches,
            "authentication": "unprotected" if algorithm == 0 else ("passed" if matches else "failed")}


def _options(ciphering, integrity):
    if ciphering is None and integrity is None:
        raise SecurityToolsError("Enable Ciphering or Integrity.")


def transmit(data, *, ciphering=None, integrity=None, enc_key=b"", int_key=b"", count=0, bearer=0, direction=0):
    _options(ciphering, integrity)
    result = {"operation": "transmit", "input_bit_length": data.length, "ciphering": ciphering, "integrity": integrity,
              "authentication": "unprotected" if integrity in (None, 0) else "generated"}
    payload = data
    if integrity is not None:
        tag = mac(integrity, int_key, count, bearer, direction, data)
        result["mac_i"] = tag.to_dict()
        if ciphering is not None:
            payload = data.concat(tag)
    if ciphering is not None:
        result["cipher_bit_length"] = payload.length
        payload = cipher(ciphering, enc_key, count, bearer, direction, payload)
    result["data"] = payload.to_dict()
    return result


def receive(data, *, ciphering=None, integrity=None, enc_key=b"", int_key=b"", count=0, bearer=0, direction=0, received_mac=None):
    _options(ciphering, integrity)
    result = {"operation": "receive", "input_bit_length": data.length, "ciphering": ciphering, "integrity": integrity,
              "authentication": "unprotected"}
    payload = data
    if ciphering is not None:
        if integrity is not None and data.length < 32:
            raise SecurityToolsError("Combined receive requires at least 32 valid bits for MAC-I.")
        payload = cipher(ciphering, enc_key, count, bearer, direction, data)
    if integrity is not None:
        if ciphering is not None:
            payload, received_mac = payload.split(payload.length - 32)
        result.update(verify(integrity, int_key, count, bearer, direction, payload, received_mac))
    result["data"] = payload.to_dict()
    return result
