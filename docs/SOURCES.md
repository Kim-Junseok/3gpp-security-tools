# 표준·공식 테스트 원문 조사

- 조사일: 2026-11-01 (Asia/Seoul)
- 문서 profile: TECHNICAL_NOTE
- 현재 상태: 원문 확보·공식 벡터 전사 완료. legacy 공식 36건 개발 실행 PASS. 상세 결과는 VALIDATION.md 참조.

## 버전 탐색

ETSI 공개 디렉터리에서 확인한 가장 높은 버전은 다음과 같다.
이를 이번 구현의 고정 기준으로 제안한다.
3GPP 포털 전체의 최신성 검증과 동일한 의미는 아니다.

| 문서 | 버전 | 원문 |
|---|---|---|
| TS 33.401 | 19.2.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/133400_133499/133401/19.02.00_60/ts_133401v190200p.pdf) |
| TS 33.501 | 19.7.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/133500_133599/133501/19.07.00_60/ts_133501v190700p.pdf) |
| TS 35.215 | 19.0.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/135200_135299/135215/19.00.00_60/ts_135215v190000p.pdf) |
| TS 35.216 | 19.0.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/135200_135299/135216/19.00.00_60/ts_135216v190000p.pdf) |
| TS 35.217 | 19.0.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/135200_135299/135217/19.00.00_60/ts_135217v190000p.pdf) |
| TS 35.221 | 19.0.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/135200_135299/135221/19.00.00_60/ts_135221v190000p.pdf) |
| TS 35.222 | 19.0.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/135200_135299/135222/19.00.00_60/ts_135222v190000p.pdf) |
| TS 35.223 | 19.0.0 | [PDF](https://www.etsi.org/deliver/etsi_ts/135200_135299/135223/19.00.00_60/ts_135223v190000p.pdf) |

위 PDF는 온라인 열람으로 버전을 확인했다.
TS 33.401·33.501과 상세 SAGE 명세·테스트 원문을 로컬에 저장했다.
TS 35.xxx PDF들은 §2의 SAGE 문서를 참조하며 §4가 그 문서에 기술 내용을 위임한다.
wrapper PDF 확보와 상세 알고리즘·벡터 확보를 구분한다.

| TS wrapper | 참조 SAGE 문서 버전 | 상세 원문 확보 상태 |
|---|---|---|
| 35.215 | UEA2/UIA2 Document 1 v2.1 | 로컬 확보, 표지 v2.1 확인 |
| 35.216 | SNOW 3G Document 2 v1.1 (2006-09-06) | 로컬 확보, 표지 v1.1 확인 |
| 35.217 | UEA2/UIA2 Document 3 v1.1 (2012-10-25) | 로컬 확보; §4 UEA2 5개 목록 대조 |
| 35.221 | EEA3/EIA3 Document 1 v1.7 | 공식 GSMA 원문은 표지 v1.8; CONTRACT CHANGE 기록 후 사용 |
| 35.222 | ZUC Document 2 v1.6 | 로컬 확보, 표지 v1.6 확인 |
| 35.223 | EEA3/EIA3 Document 3 v1.1 (2011-01-04) | 로컬 확보; §4/§5 각 5개 목록 대조 |

SNOW 3G 상세 명세의 발견 링크: [GSMA PDF](https://www.gsma.com/security/wp-content/uploads/2019/05/snow3gspec.pdf).
자료 목록 페이지는 일부 요청에서 HTTP 403을 반환했다.
아래 테스트 PDF 직접 다운로드는 성공했다.

## 로컬 캐시와 무결성

아래 PDF와 `pdftotext -layout` 결과는 `/tmp/3gpp-security-preflight/`에 있다.
이 임시 경로는 영구 보관 위치가 아니다.
승인 후 `local-specs/`로 옮기고 Git 추적에서 제외한다.

| 로컬 파일 | byte 수 | SHA-256 |
|---|---:|---|
| `ts_133401v190200p.pdf` | 1359397 | `39f5979a20979c00d6041a27100d1f598c60081d346d0771e0e3db50d5c66006` |
| `uea2-uia2-test-v11.pdf` | 335256 | `fdf3281aacb8098f7cee4461851910aeff84f8c6cbdaadca95ee9a5d63d1c677` |
| `eea3-eia3-test-v11.pdf` | 227188 | `65b461c84daac4f9c7e831b739ca33792e25fdcbcf67e2e6befa60e4a58eea82` |

UEA2/UIA2 Document 3 source:
[GSMA PDF v1.1](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/Doc3-UEA2-UIA2-Spec-Implementors-Test-Data.pdf).

EEA3/EIA3 Document 3 source:
[GSMA PDF v1.1](https://www.gsma.com/solutions-and-impact/technologies/security/wp-content/uploads/2019/05/eea3eia3testdatav11.pdf).
검색에서 발견한 `/aboutus/wp-content/uploads/2014/12/eea3eia3testdatav11.pdf` 주소는 이 URL로 redirect한다.

## 테스트 집계 범위

TS 33.401 C.1 6개, C.2 8개, C.4 7개의 본문 test set 표제를 확인했다.
SAGE UEA2/UIA2 Document 3 §4 5개와 EEA3/EIA3 Document 3 §4·§5 각 5개의 본문 표제를 확인했다.
합계 36개는 요구사항 문서가 지정한 알고리즘 입출력 suite의 필수 수이다.
SNOW 3G/ZUC primitive 내부 상태 자료는 이 수에 포함하지 않는다.
UEA2의 EEA1 입력 매핑은 TS 33.401 C.3의 설명에 근거한다.
매개변수 매핑을 문서화했고 전사한 다섯 벡터가 공식 출력과 일치했다.

고정 원문의 목록에서 Null 전용 공식 suite는 발견하지 못했고, 정의 기반 자체 테스트를 실행했다.
256-bit TS 35.240~35.248의 버전·명세·NEA/NIA 목록 확보는 후속 작업으로 남긴다.
AEAD/NCA는 제외한다.

## 원문 이용 안내와 패키징 참고

원문의 이용 조건 안내는 [ETSI](https://www.etsi.org/expertise/algorithms-codes/)와
[GSMA](https://www.gsma.com/solutions-and-impact/technologies/security/security-algorithms/)에서 확인할 수 있다.
이 저장소에는 원문 PDF와 참조 C 코드 전체를 포함하지 않는다.

패키징 방식은 [PyInstaller 공식 설명](https://www.pyinstaller.org/en/stable/operating-mode.html)을 확인했다.
조회된 문서 버전은 6.22.3이다.
빌드 성공과 깨끗한 Windows 환경에서의 실제 실행은 별도로 검증한다.

## 승인 후 원문 확보 기록

PDF 표지를 직접 읽어 실제 버전을 확인했다. 전체 표지 문자열·요청 URL·최종 URL은 [source-acquisition.json](source-acquisition.json)에 보존했다.
로컬 경로는 프로젝트 루트 기준이며 원문은 Git에서 제외한다.

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

이 표가 앞선 사전 조사 시점의 미확보 상태를 갱신한다.
EEA3/EIA3 Document 1은 TS wrapper 참조 v1.7과 달리 실제 확보 표지가 v1.8이다.
변경 이력은 integrity 최대 데이터 길이 증가를 명시한다. CONTRACT CHANGE 기록은 [TASK_CONTRACT.md](TASK_CONTRACT.md)를 따른다.

### Cip1 입력 매핑과 원문 정규화

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

### Null 검증 범위

TS 33.401 v19.2.0 B.0과 TS 33.501 v19.7.0 D.1에서 zero keystream과 32-bit zero MAC 정의를 확인했다.
고정된 공식 문서들의 알고리즘 test set 목록에는 Null 전용 suite가 없다.
Null 동작은 정의 기반 자체 테스트로 검증하고 공식 36건과 별도 집계한다.
이 관찰은 다른 모든 출처에 Null 벡터가 없다는 주장이 아니다.
