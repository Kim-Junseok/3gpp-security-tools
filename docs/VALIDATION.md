# Validation record

## v0.1.0 — 2026-11-08

This release removes the GUI footer and retains the user's shortened PDCP guidance. The calculation core and tracked official inputs/expected values are unchanged from rc7. The EXE is rebuilt from commit `c442272baafafd51f2f329a74dc7bbc53ff46f95`.

### Official vectors

| Category | Required cases |
|---|---:|
| Legacy algorithm vectors | 36 |
| 256-bit NEA/NIA vectors | 72 |
| Release 20 primitive vectors | 27 |
| **Total** | **135** |

The 63 internal-state snapshots are primitive subchecks and are not added to the total. Null definition checks, PDCP header-layout checks, integration tests, and GUI tests are counted separately. Expected values come from fixed source transcriptions; implementation outputs are not used to generate them.

| Environment | Official vectors | Evidence |
|---|---:|---|
| Linux CI | 135/135 PASS | [Report](../validation/v0.1.0/linux/official-report.json) |
| Windows CI source | 135/135 PASS | [Report](../validation/v0.1.0/windows-source/official-report.json) |
| Windows CI packaged EXE | 135/135 PASS | [Report](../validation/v0.1.0/windows-ci/official-report.json) |
| Windows 11 packaged EXE | 135/135 PASS | [Report](../validation/v0.1.0/windows/official-report.json) |

### Integration and GUI checks

| Environment | Result | Evidence |
|---|---:|---|
| Linux CI integration/boundary tests | 48 PASS | [Report](../validation/v0.1.0/linux/integration-report.json) |
| Windows CI source integration/boundary tests | 48 PASS | [Report](../validation/v0.1.0/windows-source/integration-report.json) |
| Linux CI GUI | 275/275 PASS | [Report](../validation/v0.1.0/linux/gui-report.json) |
| Windows CI source GUI | 277/277 PASS | [Report](../validation/v0.1.0/windows-source/gui-report.json) |
| Windows CI packaged EXE GUI | 277/277 PASS | [Report](../validation/v0.1.0/windows-ci/gui-report.json) |
| Windows 11 packaged EXE GUI | 277/277 PASS | [Report](../validation/v0.1.0/windows/gui-report.json) |

Integration tests cover bit framing, keys, COUNT, EXTRA_IV, MAC lengths, combined processing, tampering, and PDCP/SDAP boundaries. Header-generation tests use independent layout expectations for LTE/NR formats, COUNT/SN/HFN behavior, and direction-specific flags. They are not official packet vectors.

GUI checks cover selections, shared settings, conversion, copying, error display, automatic/manual headers, payload boundaries, and scrolling. The existing layout check now verifies that the result details remain reachable inside the canvas after removing the footer. Windows adds two checks for actual DPI awareness and the selected UI font.

### Windows execution and display

Windows CI uses Windows Server 2025 x64. The local execution check uses Windows 11 Home x64 (10.0.26200). Both checks copy the EXE alone into a temporary directory, run it from a different working directory, and clear PATH/Python/Tcl/Tk environment settings. The local check also temporarily renames the project's development Python directory, then restores it. These tests do not establish execution on a fresh PC/VM with no installed runtimes.

- [Windows CI deployment report](../validation/v0.1.0/windows-ci/deployment-report.json)
- [Windows 11 deployment report](../validation/v0.1.0/windows/deployment-report.json)

The EXE manifest and source startup use **System DPI awareness**, matching Tk 8.6. The GUI uses scalable Segoe UI/Arial text and Consolas for data. GUI tests verify the actual awareness mode and font selection, together with layout and copy controls.

The [actual packaged EXE capture](../validation/v0.1.0/gui-preview.png) was inspected on Windows 11 at 192 DPI (200% scaling). Visible English labels, numeric fields, and guidance are legible. The footer is absent; input, format, action, and output controls remain visible. Lower result details remain reachable by scrolling, as checked separately by the GUI test. [Capture metadata](../validation/v0.1.0/visual-capture.json) records the 2026 × 1711 window, DPI, and EXE hash. This visual check covers the default window; GUI tests separately exercise calculations and copying.

Display scaling at 100%, 125%, and 150%, movement between different-DPI monitors, Windows 10, ARM64, and fresh-PC/VM execution remain unverified for this release.

### Build identity and reproducibility

- [Successful CI run 42485290515](https://github.com/Kim-Junseok/3gpp-security-tools/actions/runs/42485290515).
- Build commit: `c442272baafafd51f2f329a74dc7bbc53ff46f95`.
- EXE SHA-256: `b0ddb3db01310c37d267a311898aa24b35f6e70558089e7d664e169138802dcd`.
- Windows build runtime: CPython 3.12.10 x64; PyInstaller 6.22.3.
- [Build metadata](../validation/v0.1.0/windows-ci/build-info.json) and [source comparison](../validation/v0.1.0/source-match.json): all 35 recorded input files match, allowing Git line-ending conversion.

The downloaded CI artifact ZIPs are checked against GitHub's SHA-256 digests before extraction. Release packaging checks the EXE hash, passing frozen reports, and all build inputs against the source checkout. Usage and reproducibility commands are in the [README](../README.md).

## Previous release candidates

| Version | Official vectors | Integration tests | Windows EXE GUI | Evidence |
|---|---:|---:|---:|---|
| rc7 | 135/135 | 48 | 277/277 | [Shared headers](../validation/shared-pdcp/scope.json) |
| rc6 | 135/135 | 40 | 238/238 | [PDCP boundaries](../validation/pdcp-headers/scope.json) |
| rc5 | 135/135 | 34 | 201/201 | [Windows deployment](../validation/rc5/windows/deployment-report.json) |
| rc4 | 135/135 | 31 | 199/199 | [Windows deployment](../validation/rc4/windows/deployment-report.json) |
| rc3 | 135/135 | 31 | 197/197 | [Windows deployment](../validation/rc3/windows/deployment-report.json) |
| rc2 | 36/36 | 24 | 44/44 | [Windows deployment](../validation/gui-update/windows/deployment-report.json) |
| rc1 | 36/36 | 21 | 30/30 | [Windows deployment](../validation/v0.1/windows/deployment-report.json) |

rc6–rc7 used hosted Windows CI for the updated EXE; they did not repeat local Windows 11 visual/DPI checks. rc3–rc5 also passed local Windows 11 checks with the development runtime isolated. Earlier evidence and release assets remain preserved.

The first local rc4 build was blocked before execution by Windows Code Integrity policy. It was not distributed. The [blocked-build record](../validation/rc4/local-build-blocked.json) and [build inputs](../validation/rc4/local-build-info.json) remain separate from the passing CI-built EXE used for rc4.

Earlier 200% scaling observations are retained in [rc3](../validation/rc3/visual-capture.json), [rc4](../validation/rc4/visual-capture.json), and [rc5](../validation/rc5/visual-capture.json). Those captures show source GUI windows; their EXE widget checks were recorded separately. The original source re-acquisition and hashes are preserved in [source-acquisition.json](../validation/rc3/source-acquisition.json).
