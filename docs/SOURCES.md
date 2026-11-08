# Standards and official test sources

## 256-bit NEA/NIA — Release 20

The fixed baseline is TS 35.240–35.248 v20.0.0. On 2026-11-05, the nine official ZIP/DOCX pairs obtained during cloud development were downloaded again locally. ZIP and DOCX SHA-256 values matched the tracked manifest, and the actual document text identified `V20.0.0`.

Final URLs, local paths, and both hashes are preserved in the [acquisition record](../validation/rc3/source-acquisition.json).

| Document | Actual version | Final URL | Local DOCX | DOCX SHA-256 |
|---|---|---|---|---|
| TS 35.240 | 20.0.0 | [ZIP](https://www.3gpp.org/ftp/Specs/archive/35_series/35.240/35240-k00.zip) | `local-specs/35240-k00.docx` | `b291ef04b8ff49434e407adeeb4dfeb348312f367a101a78e972454dea1db554` |
| TS 35.241 | 20.0.0 | [ZIP](https://www.3gpp.org/ftp/Specs/archive/35_series/35.241/35241-k00.zip) | `local-specs/35241-k00.docx` | `c374c669afea98893f8b451371c1913322d55b0ff5840daecc77ffb73b1816ad` |
| TS 35.242 | 20.0.0 | [ZIP](https://www.3gpp.org/ftp/Specs/archive/35_series/35.242/35242-k00.zip) | `local-specs/35242-k00.docx` | `bb1fd93f69df51d9641feedb1f61b901bfdddaa6af0a64db0854e173aaddfada` |
| TS 35.243 | 20.0.0 | [ZIP](https://www.3gpp.org/ftp/Specs/archive/35_series/35.243/35243-k00.zip) | `local-specs/35243-k00.docx` | `9b77943ca34a80890d18e54e823de6bc4163587412fe222c013cf1cfb4176109` |
| TS 35.244 | 20.0.0 | [ZIP](https://www.3gpp.org/ftp/Specs/archive/35_series/35.244/35244-k00.zip) | `local-specs/35244-k00.docx` | `331465e3014340d5dfd39dede10721c6fc0a32b9be4e48a1bf8169073f3ffb55` |
| TS 35.245 | 20.0.0 | [ZIP](https://www.3gpp.org/ftp/Specs/archive/35_series/35.245/35245-k00.zip) | `local-specs/35245-k00.docx` | `0a734b605afe8d52024516814e9a675056bcbfca82a673caf36a018fa3280ec0` |
| TS 35.246 | 20.0.0 | [ZIP](https://www.3gpp.org/ftp/Specs/archive/35_series/35.246/35246-k00.zip) | `local-specs/35246-k00.docx` | `dc07113c14fb7d1b9106e62f2109ae4b172ce0228e6cb6672cb09f93f6e18e14` |
| TS 35.247 | 20.0.0 | [ZIP](https://www.3gpp.org/ftp/Specs/archive/35_series/35.247/35247-k00.zip) | `local-specs/35247-k00.docx` | `64a3581c344dee90bae4d217f795d0dec1d2390be86358bb44345eddd657e92e` |
| TS 35.248 | 20.0.0 | [ZIP](https://www.3gpp.org/ftp/Specs/archive/35_series/35.248/35248-k00.zip) | `local-specs/35248-k00.docx` | `485d2c0eba4060dccc46952a3fa9ffdd9826ce8ff255005824b6d900dface2d2` |

- TS 35.240, 35.243, and 35.246: Algorithm specifications.
- TS 35.241, 35.244, and 35.247: Primitive implementation test data.
- TS 35.242, 35.245, and 35.248: NEA/NIA design test data; 12 NEA and 12 NIA cases from each document.

The [manifest](https://github.com/Kim-Junseok/3gpp-security-tools/blob/v0.1.0/testdata/256/manifest.json) fixes documents, sections, test sets, and all 99 required cases: 72 NEA/NIA cases and 27 primitive cases. The 63 SNOW 5G/ZUC internal-state snapshots are subchecks within six primitive cases. Repeated POLYVAL vectors are retained by source document; they are not treated as distinct independent vectors. NCA test sets are excluded.

The [transcription tool](https://github.com/Kim-Junseok/3gpp-security-tools/blob/v0.1.0/tools/import_256_vectors.py) reads document text from official DOCX XML. It does not call the calculation core or use implementation output to produce expected values. [Inputs](https://github.com/Kim-Junseok/3gpp-security-tools/blob/v0.1.0/testdata/256/inputs.json) and [expected values](https://github.com/Kim-Junseok/3gpp-security-tools/blob/v0.1.0/testdata/256/expected.json) are tracked separately in Git.

```bash
python3 tools/import_256_vectors.py --specs local-specs --output /tmp/3gpp-256-transcription
```

Use the separate output directory to compare a new transcription with tracked files, without overwriting expected values.

TS 35.240, 35.243, and 35.246 §7.2.0 describe a minimum of one message bit. Official NIA test sets 1, 4, and 5 nevertheless include empty messages. The implementation accepts zero-bit NIA input to reproduce these official cases. This interpretation is recorded in [scope.json](../validation/256-bit/scope.json).

## Legacy algorithms 0–3

The baseline uses TS 33.401 v19.2.0 and TS 33.501 v19.7.0. The wrappers TS 35.215/216/217 and TS 35.221/222/223 use v19.0.0. Actual SAGE PDF cover versions and final sources are recorded below.

| Cover version | Final URL | Local path | SHA-256 |
|---|---|---|---|
| 2.1 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/uea2uia2d1v21.pdf) | `local-specs/uea2-uia2-spec-v21.pdf` | `d2671f7821e8971e8bf4245ff50f28fa7a1ec71be29927f60ef2f436b8edf438` |
| 1.1 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/snow3gspec.pdf) | `local-specs/snow3g-spec-v11.pdf` | `a4dc79f2dcf3a1d91a0c5efbae317ffc50cbf90a9bb53da0edb52b4e86b989b5` |
| 1.6 | [PDF](https://www.gsma.com/about-us/wp-content/uploads/2014/12/eea3eia3zucv16.pdf) | `local-specs/zuc-spec-v16.pdf` | `07db149438c92b6931eb34708df81134c4fa9a89cb2e0802cb3dd2d59f8907ae` |
| 19.7.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/133500_133599/133501/19.07.00_60/ts_133501v190700p.pdf) | `local-specs/ts_133501v190700p.pdf` | `a9331407330f3aaae79c3c990f1423a330a69ea0bd4fde68e52173ac6c41ac0f` |
| 1.8 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/EEA3_EIA3_specification_v1_8.pdf) | `local-specs/eea3-eia3-spec-v18.pdf` | `b65d11ffa74c87ae6c898b48df5b36fe838297aede9c819bacb782c43695b974` |
| 19.2.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/133400_133499/133401/19.02.00_60/ts_133401v190200p.pdf) | `local-specs/ts_133401v190200p.pdf` | `39f5979a20979c00d6041a27100d1f598c60081d346d0771e0e3db50d5c66006` |
| 1.1 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/Doc3-UEA2-UIA2-Spec-Implementors-Test-Data.pdf) | `local-specs/uea2-uia2-test-v11.pdf` | `fdf3281aacb8098f7cee4461851910aeff84f8c6cbdaadca95ee9a5d63d1c677` |
| 1.1 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/eea3eia3testdatav11.pdf) | `local-specs/eea3-eia3-test-v11.pdf` | `65b461c84daac4f9c7e831b739ca33792e25fdcbcf67e2e6befa60e4a58eea82` |

The TS 35.221 wrapper refers to SAGE Document 1 v1.7, while the obtained official PDF cover identifies v1.8. Its change history increases the maximum Integrity data length. Implementation uses the acquired v1.8 specification; official EEA3/EIA3 tests use Document 3 v1.1.

| Suite | Source | Required |
|---|---|---:|
| Cip1 | TS 35.217 → SAGE Document 3 v1.1 §4; TS 33.401 C.3 mapping | 5 |
| Itg1 | TS 33.401 C.4 | 7 |
| Cip2 | TS 33.401 C.1 | 6 |
| Itg2 | TS 33.401 C.2 | 8 |
| Cip3 | TS 35.223 → SAGE Document 3 v1.1 §4 | 5 |
| Itg3 | Same SAGE document §5 | 5 |
| Total | Legacy algorithm vectors | **36** |

The legacy [manifest](https://github.com/Kim-Junseok/3gpp-security-tools/blob/v0.1.0/testdata/manifest.json), [inputs](https://github.com/Kim-Junseok/3gpp-security-tools/blob/v0.1.0/testdata/inputs.json), and [expected values](https://github.com/Kim-Junseok/3gpp-security-tools/blob/v0.1.0/testdata/expected.json) are tracked in Git.

## Cip1 mapping and source normalization

TS 33.401 C.3 maps UEA2 tests to EEA1 one-to-one.

| UEA2 | EEA1 Core | Mapping |
|---|---|---|
| CK | key | Preserve 128-bit byte order |
| COUNT-C | count | Preserve the 32-bit value |
| BEARER | bearer | Preserve the 5-bit value |
| DIRECTION | direction | Preserve the 1-bit value |
| LENGTH | Bits.length | Preserve the source bit length |
| IBS / OBS | Input / expected output | Process valid bits, MSB first |

SAGE Document 1 v2.1 §3.4 maps K3 through K0 from the first 32-bit word of the key. The SNOW initial IV uses `IV3 = IV1 = COUNT` and `IV2 = IV0 = (BEARER << 27) | (DIRECTION << 26)`.

All five official cases pass through this mapping before comparison with expected values. Independent mapping tests also check word ordering against the source K0–K3 and IV0–IV3 tables.

For Cip1-005, source page 14 prints plaintext word 19 as `60876A0`. In row 18 of the same source, XOR of the second keystream word `AE56E26E` and the second enc/dec word `A85E94CE` gives `060876A0`. Restoring the omitted leading zero preserves a 32-bit word. The page image was also inspected. The importer and manifest record this input normalization; no core output was used.

## PDCP header layouts

LTE/NR header generation and protection boundaries use the following fixed references. Their acquisition metadata and referenced figures are preserved in [shared-header scope](../validation/shared-pdcp/scope.json); the earlier boundary implementation is described in [PDCP scope](../validation/pdcp-headers/scope.json).

- [TS 36.323 v19.0.0](https://www.etsi.org/deliver/etsi_ts/136300_136399/136323/19.00.00_60/ts_136323v190000p.pdf), SHA-256: `4de27c4f098291fc975b1de02269dc8b4be67b79ff1fe3a541b6b4cd0da2849a`.
- [TS 38.323 v19.1.0](https://www.etsi.org/deliver/etsi_ts/138300_138399/138323/19.01.00_60/ts_138323v190100p.pdf), SHA-256: `a5f68eadf7025137d3de41bffe64e21d9116ddbf7a54639a5c7164776891d96e`.

Header-layout expectations come from standard layout figures and independent framing checks. They are separate from the 135 official algorithm vectors. Reassembling segments of an official algorithm message checks framing against its fixed MAC; it does not create an official PDCP packet vector.

## Null and test accounting

TS 33.401 B.0 and TS 33.501 D.1 define the Null zero keystream and 32-bit zero MAC. Definition-based tests check Null; it is not added to the official-vector total.

The official total is 36 legacy + 72 NEA/NIA + 27 primitive cases = 135. These results do not establish conformance of a full PDU parser, protocol state machine, or standard NCA procedure.
