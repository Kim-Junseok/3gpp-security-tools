"""LTE/NR PDCP Data PDU headers, TS 36.323 v19.0.0 and 38.323 v19.1.0.

COUNT = HFN || SN. Only the least significant SN bits appear in the header;
all reserved bits are zero. Control PDUs do not use this Data PDU layout and
are outside the application's ciphering/integrity pipeline.
"""

from .errors import SecurityToolsError

HEADER_SOURCES = ("Automatic", "Manual Hex")
SN_LENGTHS = {"NR DRB": (12, 18), "NR SRB": (12,),
              "LTE DRB": (7, 12, 15, 18), "LTE SRB": (5,), "LTE SLRB": (16,)}
PDU_TYPES = tuple(SN_LENGTHS)


def generate_header(count, sn_bits=12, pdu_type="NR DRB", dc=1, *, direction=0, poll=0, ailc=0, slrb_prefix=b""):
    if type(count) is not int or not 0 <= count <= 0xffffffff:
        raise SecurityToolsError("COUNT must be in 0..4294967295 (32-bit unsigned).")
    if pdu_type not in PDU_TYPES:
        raise SecurityToolsError("Choose a supported LTE/NR PDCP format, or use Manual Hex.")
    if type(sn_bits) is not int or sn_bits not in SN_LENGTHS[pdu_type]:
        allowed = ", ".join(str(n) for n in SN_LENGTHS[pdu_type])
        raise SecurityToolsError(f"{pdu_type} requires an SN length in: {allowed} bits.")
    for name, value in (("DIRECTION", direction), ("P", poll), ("AILC", ailc)):
        if type(value) is not int or value not in (0, 1):
            raise SecurityToolsError(f"{name} must be 0 or 1.")
    if poll and not (pdu_type == "LTE DRB" and sn_bits == 18 and direction == 1):
        raise SecurityToolsError("P is only available for LTE DRB with 18-bit SN in DL.")
    if ailc and not (pdu_type == "LTE DRB" and sn_bits == 12 and direction == 0):
        raise SecurityToolsError("AILC is only available for LTE DRB with 12-bit SN in UL.")
    if not isinstance(slrb_prefix, bytes):
        raise SecurityToolsError("SLRB prefix must be bytes.")
    if slrb_prefix and pdu_type != "LTE SLRB":
        raise SecurityToolsError("SLRB prefix is only available for LTE SLRB.")
    sn = count & ((1 << sn_bits) - 1)
    if pdu_type.endswith("SRB"):
        # LTE: R/R/R + 5-bit SN. NR: R/R/R/R + 12-bit SN. Neither has D/C.
        return sn.to_bytes(1 if pdu_type == "LTE SRB" else 2, "big")
    if pdu_type == "LTE SLRB":
        if len(slrb_prefix) != 3:
            raise SecurityToolsError("LTE SLRB needs its actual 3-byte SDU-type/identity prefix; COUNT alone cannot supply it.")
        return slrb_prefix + sn.to_bytes(2, "big")
    if type(dc) is not int or dc not in (0, 1):
        raise SecurityToolsError("D/C must be 0 or 1.")
    if dc == 0:
        raise SecurityToolsError("D/C=0 is a PDCP Control PDU: this Data PDU Ciphering/Integrity pipeline does not apply.")
    size = 1 if sn_bits == 7 else (3 if sn_bits == 18 else 2)
    value = (1 << (size * 8 - 1)) | sn
    if poll or ailc:
        value |= 1 << (size * 8 - 2)
    return value.to_bytes(size, "big")
