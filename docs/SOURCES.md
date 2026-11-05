# 표준·공식 테스트 출처

## 256-bit NEA/NIA — Release 20

TS 35.240~35.248 v20.0.0을 고정 기준으로 사용한다.
클라우드에서 확보한 원문 기록을 바탕으로 2026-11-05에 공식 ZIP과 DOCX 9개를 로컬에 다시 내려받았다.
추적 중인 manifest의 ZIP·DOCX SHA-256과 실제 문서의 `V20.0.0` 문구를 대조했다.
최종 URL·로컬 경로·두 파일 해시는 [확보 기록](../validation/rc3/source-acquisition.json)에 보존한다.

| 문서 | 실제 버전 | 최종 URL | 로컬 DOCX | DOCX SHA-256 |
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

- TS 35.240·35.243·35.246: 알고리즘 명세.
- TS 35.241·35.244·35.247: primitive 구현 검증 데이터.
- TS 35.242·35.245·35.248: NEA/NIA 설계 검증 데이터. 각 문서에서 NEA 12건·NIA 12건을 사용한다.

[manifest](https://github.com/Kim-Junseok/3gpp-security-tools/blob/main/testdata/256/manifest.json)에 문서·절·test set과 필수 99건을 고정했다.
NEA/NIA 72건과 primitive 27건을 구분한다.
SNOW 5G·ZUC 내부 상태 snapshot 63건은 6개 primitive 케이스 내부의 하위 검사다.
세 문서에 반복된 POLYVAL 벡터는 출처별로 보존하며 새로운 독립 벡터로 해석하지 않는다.
NCA test set은 가져오지 않는다.

[전사 도구](https://github.com/Kim-Junseok/3gpp-security-tools/blob/main/tools/import_256_vectors.py)는 공식 DOCX XML의 문서 텍스트를 읽는다.
계산 코어를 호출하거나 구현 출력으로 기대값을 만들지 않는다.
입력과 기대값은 [inputs.json](https://github.com/Kim-Junseok/3gpp-security-tools/blob/main/testdata/256/inputs.json)·[expected.json](https://github.com/Kim-Junseok/3gpp-security-tools/blob/main/testdata/256/expected.json)으로 분리해 Git으로 추적한다.

```bash
python3 tools/import_256_vectors.py --specs local-specs --output /tmp/3gpp-256-transcription
```

위 명령의 출력 경로는 원문 재전사 대조용이다. 기존 expected를 덮어쓰지 않고 추적 파일과 비교한다.
TS 35.240·35.243·35.246 §7.2.0의 최소 1-bit 설명과 달리 공식 NIA test 1·4·5에는 빈 메시지가 포함돼 있다.
현재 구현은 이 공식 케이스를 재현하도록 0-bit NIA 입력을 허용한다.
이 해석은 [구현 범위 기록](../validation/256-bit/scope.json)에 남겨져 있다.

## Legacy 0~3

TS 33.401 v19.2.0과 TS 33.501 v19.7.0을 기준으로 삼는다.
TS 35.215·35.216·35.217 및 TS 35.221·35.222·35.223의 wrapper 버전은 v19.0.0이다.
상세 SAGE 원문의 실제 표지 버전과 최종 출처는 다음과 같다.

| 표지 버전 | 최종 URL | 로컬 경로 | SHA-256 |
|---|---|---|---|
| 2.1 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/uea2uia2d1v21.pdf) | `local-specs/uea2-uia2-spec-v21.pdf` | `d2671f7821e8971e8bf4245ff50f28fa7a1ec71be29927f60ef2f436b8edf438` |
| 1.1 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/snow3gspec.pdf) | `local-specs/snow3g-spec-v11.pdf` | `a4dc79f2dcf3a1d91a0c5efbae317ffc50cbf90a9bb53da0edb52b4e86b989b5` |
| 1.6 | [PDF](https://www.gsma.com/about-us/wp-content/uploads/2014/12/eea3eia3zucv16.pdf) | `local-specs/zuc-spec-v16.pdf` | `07db149438c92b6931eb34708df81134c4fa9a89cb2e0802cb3dd2d59f8907ae` |
| 19.7.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/133500_133599/133501/19.07.00_60/ts_133501v190700p.pdf) | `local-specs/ts_133501v190700p.pdf` | `a9331407330f3aaae79c3c990f1423a330a69ea0bd4fde68e52173ac6c41ac0f` |
| 1.8 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/EEA3_EIA3_specification_v1_8.pdf) | `local-specs/eea3-eia3-spec-v18.pdf` | `b65d11ffa74c87ae6c898b48df5b36fe838297aede9c819bacb782c43695b974` |
| 19.2.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/133400_133499/133401/19.02.00_60/ts_133401v190200p.pdf) | `local-specs/ts_133401v190200p.pdf` | `39f5979a20979c00d6041a27100d1f598c60081d346d0771e0e3db50d5c66006` |
| 1.1 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/Doc3-UEA2-UIA2-Spec-Implementors-Test-Data.pdf) | `local-specs/uea2-uia2-test-v11.pdf` | `fdf3281aacb8098f7cee4461851910aeff84f8c6cbdaadca95ee9a5d63d1c677` |
| 1.1 | [PDF](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/eea3eia3testdatav11.pdf) | `local-specs/eea3-eia3-test-v11.pdf` | `65b461c84daac4f9c7e831b739ca33792e25fdcbcf67e2e6befa60e4a58eea82` |

TS 35.221 wrapper의 참조는 SAGE Document 1 v1.7이지만 실제 확보한 공식 PDF 표지는 v1.8이다.
변경 이력은 integrity 최대 데이터 길이 증가를 명시한다.
구현 명세는 확보한 v1.8, 공식 EEA3/EIA3 테스트 기준은 Document 3 v1.1을 사용했다.

| Suite | 원문 | 필수 수 |
|---|---|---:|
| Cip1 | TS 35.217 → SAGE Document 3 v1.1 §4; TS 33.401 C.3 매핑 | 5 |
| Itg1 | TS 33.401 C.4 | 7 |
| Cip2 | TS 33.401 C.1 | 6 |
| Itg2 | TS 33.401 C.2 | 8 |
| Cip3 | TS 35.223 → SAGE Document 3 v1.1 §4 | 5 |
| Itg3 | 같은 SAGE 문서 §5 | 5 |
| 합계 | legacy 알고리즘 입출력 | **36** |

Legacy 목록은 [manifest](https://github.com/Kim-Junseok/3gpp-security-tools/blob/main/testdata/manifest.json), 입력·기대값은 별도 JSON으로 추적한다.

## Cip1 입력 매핑과 원문 정규화

TS 33.401 C.3은 UEA2 테스트를 EEA1에 일대일로 대응시킨다.

| UEA2 | EEA1 Core | 대응 규칙 |
|---|---|---|
| CK | key | 128-bit byte 순서 보존 |
| COUNT-C | count | 32-bit 값 그대로 |
| BEARER | bearer | 5-bit 값 그대로 |
| DIRECTION | direction | 1-bit 값 그대로 |
| LENGTH | Bits.length | 원문 bit 길이 그대로 |
| IBS / OBS | 입력 / 기대 출력 | MSB 우선 유효 bit만 처리 |

SAGE Document 1 v2.1 §3.4의 K3..K0는 key의 앞쪽 32-bit부터 대응한다.
SNOW 초기 IV의 IV3=IV1=COUNT이고 IV2=IV0=(BEARER<<27)|(DIRECTION<<26)이다.
공식 다섯 케이스는 해당 매핑을 거쳐 expected와 비교한다.
원문의 K0..K3·IV0..IV3 표와 독립 매핑 테스트를 추가해 word 순서도 확인한다.

Cip1-005의 원문 p14에는 plaintext word 19가 `60876A0`로 인쇄돼 있다.
동일 원문 row 18에서 두 번째 keystream `AE56E26E`와 두 번째 enc/dec `A85E94CE`를 XOR하면 `060876A0`이다.
32-bit word의 생략된 선행 0을 복구한다. 원문 페이지 이미지도 대조했다.
이 입력 정규화는 importer와 manifest에 명시했으며 Core의 출력은 사용하지 않았다.

## Null과 집계 범위

TS 33.401 B.0과 TS 33.501 D.1에서 Null의 zero keystream·32-bit zero MAC 정의를 확인했다.
Null은 정의 기반 자체 테스트로 검사하며 공식 벡터 135건에 더하지 않는다.
공식 벡터 합계는 legacy 36 + NEA/NIA 72 + primitive 27이다.
입력 PDU의 보호 영역 구성이나 표준 NCA 기능의 검증으로 확대해 해석하지 않는다.
