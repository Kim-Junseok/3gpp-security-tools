# 표준·공식 테스트 원문 조사

- 조사일: 2026-11-01 (Asia/Seoul)
- 문서 profile: TECHNICAL_NOTE
- 현재 상태: 버전 및 지정 알고리즘 test set 목록 확인. 전체 벡터 전사·검증 실행 전.

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
그중 TS 33.401은 로컬에도 저장했다.
TS 35.xxx PDF들은 §2의 SAGE 문서를 참조하며 §4가 그 문서에 기술 내용을 위임한다.
wrapper PDF 확보와 상세 알고리즘·벡터 확보를 구분한다.

| TS wrapper | 참조 SAGE 문서 버전 | 상세 원문 확보 상태 |
|---|---|---|
| 35.215 | UEA2/UIA2 Document 1 v2.1 | 미확보; 해당 구현 전 필요 |
| 35.216 | SNOW 3G Document 2 v1.1 (2006-09-06) | 링크 발견, 로컬 미확보 |
| 35.217 | UEA2/UIA2 Document 3 v1.1 (2012-10-25) | 로컬 확보; §4 UEA2 5개 목록 대조 |
| 35.221 | EEA3/EIA3 Document 1 v1.7 | 미확보; 해당 구현 전 필요 |
| 35.222 | ZUC Document 2 v1.6 | 미확보; 해당 구현 전 필요 |
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
정확한 매개변수 매핑과 각 벡터 값 대조는 전사 단계에서 수행한다.

Null 공식 벡터 유무 확인과 정의 기반 테스트 설계가 남았다.
256-bit TS 35.240~35.248의 버전·명세·NEA/NIA 목록 확보는 후속 작업으로 남긴다.
AEAD/NCA는 제외한다.

## 공개 조건과 패키징 참고

원문에는 저작권과 알고리즘 사용 조건 안내가 있다.
이번 조사는 공개 가능한 벡터 범위나 알고리즘 사용 권한을 확정하지 않았다.
원문 전체와 참조 코드는 공개 저장소에 복사하지 않는다.
요구사항에 따라 공개용 벡터·구현의 조건을 확인한 후 해당 근거를 기록한다.

패키징 방식은 [PyInstaller 공식 설명](https://www.pyinstaller.org/en/stable/operating-mode.html)을 확인했다.
조회된 문서 버전은 6.22.3이다.
빌드 성공과 깨끗한 Windows 환경에서의 실제 실행은 별도로 검증한다.
