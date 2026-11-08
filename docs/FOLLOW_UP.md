# Follow-up work

## Remaining environment checks

- Run the standalone EXE on a fresh Windows PC/VM without a previous Python or development-tool installation.
- Move the window between monitors with different DPI settings and check clarity, layout, and copy controls.
- Test any display scaling settings not recorded in [VALIDATION.md](VALIDATION.md).
- Windows 10 and ARM64 remain outside the verified execution scope.

## Implemented

- Algorithms 0–6, including 256-bit NEA4/NIA4, NEA5/NIA5, and NEA6/NIA6.
- Exact Hex/Bit lengths, independent keys, variable MAC lengths, and a shared calculation core.
- A single receive input containing payload plus MAC-I.
- PDCP/Raw modes, separate headers, shared header settings, and LTE/NR header generation from COUNT/SN.
- A shorter GUI without the footer explanation, and English public documentation.

AEAD/NCA, full PDU parsing/state machines, and automatic UDC variants remain excluded. Tested behavior and environments are recorded in [VALIDATION.md](VALIDATION.md).
