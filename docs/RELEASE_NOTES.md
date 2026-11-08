# Release notes

## v0.1.0 — First stable release

- Remove the footer explanation and retain the user's shortened PDCP guidance.
- Publish the README, usage instructions, sources, validation notes, and follow-up work in English.
- Include algorithms 0–6, independent and combined processing, exact Hex/Bit handling, and shared transmit/receive settings.
- Include PDCP/Raw input modes, separate PDCP/SDAP headers, and automatic LTE/NR PDCP header generation introduced in rc6–rc7.

Download the Windows x64 ZIP, extract it, and run the EXE. Python and additional library installation are not required. See [VALIDATION.md](VALIDATION.md) for this release's results, build identity, and unverified environments.

## v0.1.0-rc7 — Shared headers and LTE/NR header generation

- Share all PDCP/SDAP values and generation settings between tabs; retain separate payloads.
- Generate the PDCP header from COUNT's low SN bits, using the selected LTE/NR bearer format.
- Support NR SRB/DRB and LTE SRB/DRB/SLRB layouts, with applicable D/C, P, AILC, and SLRB-prefix fields.
- Preserve Manual Hex input and reject automatic Control PDU generation.

Official vectors: 135/135. Integration tests: 48. Linux GUI: 275/275. Windows source/EXE GUI: 277/277. Windows execution used hosted Windows Server 2025 CI; Windows 11 visual/DPI checks were not repeated for rc7. [Evidence](../validation/shared-pdcp/scope.json)

## v0.1.0-rc6 — PDCP Integrity headers and byte lengths

- Add PDCP/Raw modes and explicit PDCP/SDAP header inputs.
- Include headers in Integrity input while keeping them outside Ciphering and payload input/output.
- Display exact byte and remaining-bit lengths.

Official vectors: 135/135. Integration tests: 40. Linux GUI: 236/236. Windows GUI: 238/238. [Evidence](../validation/pdcp-headers/scope.json)

## v0.1.0-rc5 — Unified receive input

Remove the separate `Received MAC-I` entry. Integrity-only receive accepts Data + MAC-I. Combined receive decrypts before extracting MAC-I. Details show extracted and recalculated values. The explicit Python `received_mac=` API remains available.

Official vectors: 135/135. Integration tests: 34. Windows EXE GUI: 201/201. The EXE also passed Windows 11 execution with the development runtime isolated. [Evidence](../validation/rc5/windows/deployment-report.json)

## v0.1.0-rc4 — Responsive notice wrapping

Fit guidance and error wrapping to the available width. Verify single-line display in wide windows and wrapping in narrow windows. The calculation core and official data remain unchanged.

Official vectors: 135/135. Integration tests: 31. Windows EXE GUI: 199/199. Ship the CI-built EXE that passed local Windows 11 checks. The earlier local build was blocked before execution by Windows Code Integrity policy; its evidence remains recorded separately. [Validation history](VALIDATION.md)

## v0.1.0-rc3 — English GUI and 256-bit NEA/NIA

Add algorithms 4–6, 48-bit EXTRA_IV, and 4–16-byte MAC-I lengths. Switch the GUI to English and add scrolling for small windows.

Official vectors: 135/135, comprising 36 legacy, 72 NEA/NIA, and 27 primitive cases. Integration tests: 31. Windows EXE GUI: 197/197. The CI-built EXE also passed local Windows 11 checks. [Evidence](../validation/rc3/windows/deployment-report.json)

## v0.1.0-rc2 — Display and input improvements

Add system-DPI awareness, uppercase byte-spaced Hex, Decimal/Hex/Bit COUNT, and shared radio/key settings between tabs. The GUI was Korean at this stage; the window was checked at 200% scaling.

Official vectors: 36/36. Integration tests: 24. Windows EXE GUI: 44/44. [Evidence](../validation/gui-update/windows/deployment-report.json)

## v0.1.0-rc1 — Windows GUI candidate

Provide independent legacy 0–3 Ciphering/Integrity and combined MAC-then-encrypt processing. Preserve leading zeros and non-byte-aligned inputs.

Official vectors: 36/36. Integration tests: 21. Windows EXE GUI: 30/30. Windows 11 tests copied the EXE alone and isolated the development runtime. [Evidence](../validation/v0.1/windows/deployment-report.json)

Historical release tags and assets remain unchanged. Full specifications and reference C sources are not bundled. Reference versions, hashes, and the Cip1 mapping are recorded in [SOURCES.md](SOURCES.md).
