"""Common calculation API used by GUI and official validation."""

from hmac import compare_digest
from .bits import Bits
from .errors import SecurityToolsError, UnsupportedAlgorithm


def key_bits(algorithm):
    if type(algorithm) is not int or algorithm not in range(7):
        raise UnsupportedAlgorithm("Choose algorithm 0–6. NCA is excluded.")
    return 0 if algorithm == 0 else (128 if algorithm < 4 else 256)


def mac_bits(algorithm, mac_bytes=4):
    key_bits(algorithm)
    if type(mac_bytes) is not int or not 4 <= mac_bytes <= 16:
        raise SecurityToolsError("MAC length must be an integer in 4..16 bytes.")
    if algorithm < 4 and mac_bytes != 4:
        raise SecurityToolsError("Legacy Integrity requires a 4-byte (32-bit) MAC-I.")
    return mac_bytes * 8


def _validate(algorithm, key, count, bearer, direction, data, extra_iv):
    required = key_bits(algorithm)
    for name, value, maximum in [("COUNT", count, 2**32 - 1), ("BEARER", bearer, 31), ("DIRECTION", direction, 1)]:
        if type(value) is not int or not 0 <= value <= maximum:
            raise SecurityToolsError(f"{name} must be an integer in 0..{maximum}.")
    if not isinstance(data, Bits):
        raise SecurityToolsError("Core data must include its valid bit length (Bits).")
    if required and (not isinstance(key, bytes) or len(key) * 8 != required):
        raise SecurityToolsError(f"Algorithm {algorithm} requires an exact {required}-bit key.")
    if not isinstance(extra_iv, bytes) or len(extra_iv) != 6:
        raise SecurityToolsError("EXTRA_IV must contain exactly 6 bytes (48 bits).")
    if algorithm < 4 and any(extra_iv):
        raise SecurityToolsError("EXTRA_IV is only available for algorithms 4–6.")
    if algorithm >= 4 and data.length > 2**32 - 1:
        raise SecurityToolsError("NEA/NIA accepts at most 2^32-1 message bits.")


def _module(algorithm):
    if algorithm == 2:
        from .algorithms import aes
        return aes
    if algorithm == 1:
        from .algorithms import snow
        return snow
    from .algorithms import zuc
    return zuc


def cipher(algorithm, key, count, bearer, direction, data, *, extra_iv=bytes(6)):
    _validate(algorithm, key, count, bearer, direction, data, extra_iv)
    if algorithm == 0:
        return data
    if algorithm >= 4:
        from .algorithms import nea_nia
        return nea_nia.cipher(algorithm, key, count, bearer, direction, data, extra_iv)
    return _module(algorithm).cipher(key, count, bearer, direction, data)


def mac(algorithm, key, count, bearer, direction, data, *, extra_iv=bytes(6), mac_bytes=4):
    _validate(algorithm, key, count, bearer, direction, data, extra_iv)
    mac_bits(algorithm, mac_bytes)
    if algorithm == 0:
        return Bits(bytes(4), 32)
    if algorithm >= 4:
        from .algorithms import nea_nia
        return nea_nia.mac(algorithm, key, count, bearer, direction, data, extra_iv, mac_bytes)
    return _module(algorithm).mac(key, count, bearer, direction, data)


def verify(algorithm, key, count, bearer, direction, data, received_mac, *, extra_iv=bytes(6), mac_bytes=4):
    length = mac_bits(algorithm, mac_bytes)
    if not isinstance(received_mac, Bits) or received_mac.length != length:
        raise SecurityToolsError(f"Received MAC-I must contain exactly {length} bits.")
    calculated = mac(algorithm, key, count, bearer, direction, data, extra_iv=extra_iv, mac_bytes=mac_bytes)
    matches = compare_digest(calculated.buffer, received_mac.buffer)
    return {"received_mac": received_mac.to_dict(), "calculated_mac": calculated.to_dict(),
            "matches": matches, "authenticated": algorithm != 0 and matches,
            "authentication": "unprotected" if algorithm == 0 else ("passed" if matches else "failed")}


def _options(ciphering, integrity, data):
    if ciphering is None and integrity is None:
        raise SecurityToolsError("Enable Ciphering or Integrity.")
    if not isinstance(data, Bits):
        raise SecurityToolsError("Core data must include its valid bit length (Bits).")


def _extra_for(algorithm, extra_iv):
    # The shared radio settings may combine a legacy function with a new one.
    return extra_iv if key_bits(algorithm) == 256 else bytes(6)


def _extra_option(extra_iv):
    if not isinstance(extra_iv, bytes) or len(extra_iv) != 6:
        raise SecurityToolsError("EXTRA_IV must contain exactly 6 bytes (48 bits).")


def transmit(data, *, ciphering=None, integrity=None, enc_key=b"", int_key=b"", count=0, bearer=0, direction=0,
             extra_iv=bytes(6), mac_bytes=4):
    _options(ciphering, integrity, data)
    _extra_option(extra_iv)
    result = {"operation": "transmit", "input_bit_length": data.length, "ciphering": ciphering, "integrity": integrity,
              "authentication": "unprotected" if integrity in (None, 0) else "generated"}
    payload = data
    if integrity is not None:
        tag = mac(integrity, int_key, count, bearer, direction, data,
                  extra_iv=_extra_for(integrity, extra_iv), mac_bytes=mac_bytes)
        result["mac_i"] = tag.to_dict()
        if ciphering is not None:
            payload = data.concat(tag)
    if ciphering is not None:
        result["cipher_bit_length"] = payload.length
        payload = cipher(ciphering, enc_key, count, bearer, direction, payload,
                         extra_iv=_extra_for(ciphering, extra_iv))
    result["data"] = payload.to_dict()
    return result


def receive(data, *, ciphering=None, integrity=None, enc_key=b"", int_key=b"", count=0, bearer=0, direction=0,
            received_mac=None, extra_iv=bytes(6), mac_bytes=4):
    _options(ciphering, integrity, data)
    _extra_option(extra_iv)
    tag_length = mac_bits(integrity, mac_bytes) if integrity is not None else 0
    result = {"operation": "receive", "input_bit_length": data.length, "ciphering": ciphering, "integrity": integrity,
              "authentication": "unprotected"}
    payload = data
    if ciphering is not None:
        if integrity is not None and data.length < tag_length:
            raise SecurityToolsError(f"Combined receive requires at least {tag_length} valid bits for MAC-I.")
        payload = cipher(ciphering, enc_key, count, bearer, direction, data,
                         extra_iv=_extra_for(ciphering, extra_iv))
    if integrity is not None:
        if ciphering is not None:
            payload, received_mac = payload.split(payload.length - tag_length)
        result.update(verify(integrity, int_key, count, bearer, direction, payload, received_mac,
                             extra_iv=_extra_for(integrity, extra_iv), mac_bytes=mac_bytes))
    result["data"] = payload.to_dict()
    return result
