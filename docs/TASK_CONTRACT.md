# TASK CONTRACT — 3GPP Security Tools v0.1

- 작성일: 2026-11-01 (Asia/Seoul)
- 상태: **APPROVED — 2026-11-01 사용자 지시로 재승인 대기 없이 실행**
- 문서 profile: TECHNICAL_NOTE
- 요구사항: `/home/jjuns/3GPP_SECURITY_TOOLS_PROJECT_BRIEF.md` (2026-11-01 정리본)
- 작성 기준: `/home/jjuns/.codex/TECHNICAL_WRITING_STYLE.md`

## 목적과 검증 질문

Python이나 별도 라이브러리를 설치하지 않고 실행하는 Windows GUI를 구현한다.
GUI와 공식 테스트 실행기는 동일한 Python 계산 코어를 호출한다.
검증 질문은 “legacy 0~3 연산이 고정 원문의 기대값과 일치하며, GUI와 배포 실행 파일에서도 입력의 유효 bit와 연산 순서가 보존되는가?”이다.

## 기준선과 저장소

기존에 승인된 실행 코드·결과·배포물은 발견하지 못했다.
홈 디렉터리는 Git 작업 트리가 아니다.
로컬 파일 검색과 연결된 GitHub의 `3gpp security` 저장소 검색에서 대상 저장소를 찾지 못했다.
따라서 `/home/jjuns/3gpp-security-tools`를 새 프로젝트 경로로 제안한다.
현재 이 경로에는 사전 조사 문서만 작성한다.
승인 후 로컬 Git 저장소를 초기화한다.
공개 원격 저장소와 Release 목적지는 아직 미확정이다.

## 입력과 출처

원문 목록, URL, 확보 상태, SHA-256은 [SOURCES.md](SOURCES.md)에 기록한다.
2026-11-01에 확인한 ETSI 공개 목록을 버전 탐색 기준으로 사용했다.
3GPP 포털 전체에서 이보다 새로운 버전이 없다는 주장은 하지 않는다.
아래 버전을 이번 구현의 고정 기준으로 제안한다.

| Suite | 고정 출처 | 필수 케이스 | 원문 test set |
|---|---|---:|---|
| Cip1 | TS 35.217 v19.0.0 → SAGE Document 3 v1.1 (2012-10-25), §4 | 5 | 1~5 |
| Itg1 | TS 33.401 v19.2.0 C.4 | 7 | 1~7 |
| Cip2 | TS 33.401 v19.2.0 C.1 | 6 | 1~6 |
| Itg2 | TS 33.401 v19.2.0 C.2 | 8 | 1~8 |
| Cip3 | TS 35.223 v19.0.0 → SAGE Document 3 v1.1 (2011-01-04), §4 | 5 | 1~5 |
| Itg3 | 위 SAGE Document 3 v1.1, §5 | 5 | 1~5 |
| 합계 | 요구사항에 지정된 알고리즘 입출력 테스트 | **36** | 누락 불가 |

상기 표의 합계는 알고리즘 입출력 케이스 수이다.
SNOW 3G/ZUC 내부 상태 테스트나 다른 문서의 conformance 테스트를 포함하는 수가 아니다.
보조 primitive 테스트를 추가하면 별도 집계한다.
Null은 TS 33.401 및 TS 33.501 v19.7.0의 정의를 확인한 뒤 자체 규칙 테스트로 집계한다.
Null 공식 벡터의 존재 여부는 아직 확정하지 않았다.
원문에는 도달했지만 입력·expected 전체 전사와 대조는 아직 수행하지 않았다.

## 고정 입력·가변 입력·파생량

- 고정: 1차 알고리즘 0~3, 128-bit 비Null 키, 32-bit MAC-I, 위 공식 목록과 버전, MSB 우선 bit 순서.
- 고정: 결합 송신은 MAC 생성 → 유효 bit 뒤 MAC 연결 → 전체 ciphering이다.
- 고정: 결합 수신은 deciphering → 마지막 유효 32-bit 분리 → 나머지 데이터로 MAC 재계산·비교이다.
- 가변: 송신/수신, Ciphering/Integrity 사용 여부와 각 번호, 별도 K_enc/K_int, COUNT, BEARER, DIRECTION, 데이터, Hex/Bit 형식, 독립 수신 MAC.
- 범위: COUNT 0~2^32−1, BEARER 0~31, DIRECTION 0/1. Null에서 불필요한 키는 요구하지 않는다.
- 파생: 사용자 Hex 입력은 byte 수×8, Bit 입력은 유효 문자 수를 LENGTH로 계산한다.
- 파생: 공식 실행기는 원문의 LENGTH를 보존한다. 마지막 byte의 미사용 하위 bit만 비교에서 제외한다.
- 파생: 결합 송신 ciphering 길이는 L+32, 결합 수신 데이터 길이는 전체 길이−32이다.
- 앞쪽 0을 보존한다. 비정렬 bit를 Hex로 변환하기 위해 padding하지 않는다.
- 수신 탭은 UL/DL 값을 반전하지 않는다.
- ‘사용 안 함’은 단계 생략, 알고리즘 0은 Null 연산이다. Null 비교를 인증 성공으로 표시하지 않는다.

## 기존 파일·API와 구현 선택

현재 관련 기존 파일은 요구사항 문서와 이 사전 조사 문서들이다.
재사용할 프로젝트 API는 발견하지 못했다.
다음 경계를 새로 구현한다. 함수명은 같은 의미를 유지하는 범위에서 조정할 수 있다.

| 구성 | 책임과 예정 API |
|---|---|
| `src/security_tools/bits.py` | buffer+유효 길이, parse/format/concat/split |
| `src/security_tools/core.py` | `cipher`, `mac`, `verify`, `transmit`, `receive`; 구조화된 결과·오류 |
| `src/security_tools/algorithms/` | Pure Python AES, SNOW 3G, ZUC 및 3GPP 매개변수 구성 |
| `src/security_tools/gui.py` | Tkinter/ttk 송신·수신 탭, 필요한 필드 활성화, 형식 변환·복사 |
| `src/security_tools/validation.py` | 공식 manifest·입력·expected 읽기, 동일 Core 실행, actual·비교 보고서 저장 |
| `tests/` | 자체 경계·통합·GUI 테스트. 공식 테스트와 별도 집계 |
| `packaging/` | Windows 빌드와 배포 EXE 검증 스크립트 |

계산 코어에는 외부 native 암호 확장을 도입하지 않는다.
Tkinter는 Python 배포판의 Tcl/Tk를 이용하므로 GUI 패키지 의존성을 줄일 수 있다.
PyInstaller는 Windows에서 실행해 CPython/Tcl/Tk를 함께 묶는다.
조사한 공식 문서의 PyInstaller 버전은 6.22.3이다.
실제 개발용 Windows Python patch 버전과 패키징 의존성은 설치 시 정확히 고정·기록한다.
일차 배포 대상은 Windows 11 x64로 제안한다.
Windows 10 및 ARM64는 실제 시험 전 지원 환경으로 표시하지 않는다.
단일 EXE를 먼저 시도하고, 실패 원인이 확인되면 런타임을 포함한 portable ZIP으로 전환할 수 있다.
이 전환은 사용자 추가 설치 없음이라는 요구사항을 유지하는 일반 패키징 선택이다.

## 처리 경로

GUI widget → 입력 adapter → 유효 bit와 매개변수 검사 → 공통 Core → 결과 adapter → 표시·복사 순서로 처리한다.
공식 테스트는 manifest → 입력 Set 및 독립 expected Set → 공통 Core → actual Answer Set → bit 단위 비교 순서로 처리한다.
Core는 widget, print, 파일 입출력에 의존하지 않고 JSON 직렬화 가능한 결과를 반환한다.
입력 오류·미지원 알고리즘·실행 오류·벡터 미확보·기대값 불일치를 구분한다.

## 실행 순서와 예상 산출물

1. 승인된 범위로 Git 초기화, `local-specs/` 추적 제외, 원문/해시 보존, 케이스 manifest 및 expected 전사·대조.
2. bit 처리와 Cip2/Itg2, 공식 14건 실행, 최소 GUI 연결.
3. Windows 개발 런타임 확보, 최소 GUI EXE 빌드·실행 및 패키징된 코어의 공식 검증 경로 확인.
4. Cip0/Itg0, Cip1/Itg1, Cip3/Itg3와 공식 회귀 검증.
5. 모든 0~3 결합과 전체 GUI, 자체 통합·GUI 검증.
6. 최종 Windows EXE의 공식 테스트, 다른 작업 폴더 실행, 개발 런타임 없는 환경 검증.
7. actual·보고서·재현 명령·README·배포 ZIP/EXE·checksum·진행 기록 정리.

원격 공개가 가능하면 소스와 배포 준비물을 공개 저장소/Release에 반영한다.
원격 목적지 또는 접근 권한이 없으면 로컬 배포 준비물과 정확한 차단 사유를 남긴다.

## 검증 방법과 정량 수락 기준

- 공식 기준: **36/36 PASS**, FAIL/ERROR/SKIP/BLOCKED 모두 0. 분모를 실행된 수로 축소하지 않는다.
- 원문 기대값을 전사하며 계산 코어 출력으로 expected를 만들지 않는다.
- 각 실패에 suite/case/source ID, expected/actual, 유효 길이와 첫 불일치 bit를 기록한다.
- 자체 통합: 4×4=16 조합을 byte 정렬·비정렬 입력으로 각각 시험한다. 서로 다른 두 키를 사용한다.
- 결합 참조: production transmit/receive/concat/split을 호출하지 않는 bit 문자열 기반 참조 조립과, 공식 벡터로 검증한 개별 cipher/MAC 호출로 연결 결과를 대조한다.
- 자체 통합: 비Null integrity 12조합×2정렬에서 데이터 영역과 MAC 영역 변조를 각각 검사한다. 원본 복원만으로 정확성을 판정하지 않는다.
- 경계: 32-bit 미만 결합 수신 거부, 앞쪽 0 보존, 사용자 Hex 홀수 digit 거부, 비정렬 Bit→Hex 거부, 매개변수 범위 위반, Null과 단계 생략 구분.
- GUI: 두 탭×세 보호 조합의 실행, 두 기능 해제 시 비활성화, 키/수신 MAC 활성화, 길이·변환·복사, 검증 실패 데이터 표시를 확인한다.
- GUI 입력 경로의 결과를 동일 Core 직접 호출과 비교한다. widget 실제 실행 검증과 adapter 테스트를 구분한다.
- Windows: 배포된 코어로 공식 36건 실행, EXE 창 표시 및 대표 연산, 다른 CWD 실행을 확인한다.
- 사용자가 Python을 설치하지 않아도 되는지 개발 Python/Tcl/Tk에 의존하지 않는 시험 환경에서 확인한다. 깨끗한 환경을 마련하지 못하면 해당 항목은 미검증이다.
- 위 조건과 요구사항 문서 §7을 모두 충족해야 첫 GUI 버전 완료로 표시한다.

## 미확인 사항·가정·차단과 중단 조건

| 항목 | 현재 근거·처리 |
|---|---|
| 구현 승인 | **APPROVED**. 사용자가 SOURCES.md와 확보 계획을 수용하고 추가 사항 반영 후 재승인 없이 구현하도록 지시했다. |
| 전용 preflight skill | 검색한 로컬 skill 경로에서 파일을 찾지 못했다. 사용자 메시지에 명시된 workflow와 계약 항목을 직접 적용했다. |
| 상세 SNOW/ZUC 명세 | TS wrapper가 지정한 SAGE v2.1/v1.1/v1.7/v1.6 원문 확보가 남았다. 해당 알고리즘 구현 전 확보한다. |
| Windows Python | PATH에는 WindowsApps alias만 발견했다. 실제 설치를 확인하지 못했다. 승인 후 프로젝트 개발용 Windows CPython+Tcl/Tk 설치 또는 Windows CI를 준비한다. |
| Windows 실행 | Windows 11 Home x64 조회 성공. 일반 sandbox의 WSL interop은 소켓 오류, read-only escalation에서는 성공. GUI/EXE는 아직 미검증. |
| Linux GUI | Python 3.12.3에 tkinter 없음. 승인 후 프로젝트 개발용 GUI 환경을 마련한다. |
| 공개 조건 | 표준 원문은 Git에서 제외한다. 원문·벡터·참조 코드의 사용/재배포 조건을 확인하고 근거를 남긴다. 공개 가능성을 아직 확정하지 않았다. |
| 공개 저장소 | 검색에서 대상이 확인되지 않았다. 로컬 작업은 진행 가능하다. 공개 목적지가 필요한 단계에서만 사용자 정보를 요청한다. |

공식 자료를 확보하지 못하면 해당 suite를 BLOCKED로 기록하고 독립 작업을 계속한다.
공식 기대값 불일치는 원문 대조와 구현 조사로 해결한다.
skip, xfail, 비교 길이 축소 또는 입력별 정답 하드코딩으로 통과 처리하지 않는다.
실제 Windows 시험이 불가능하면 배포 검증 완료를 선언하지 않는다.
모델·공식 목록·비교 의미·범위 변경이 필요하면 영향을 받는 작업을 멈추고 CONTRACT CHANGE를 보고한다.
256-bit NEA/NIA는 후속 목록으로만 관리하고 AEAD/NCA는 구현하지 않는다.
NAS/PDCP 파싱과 표준 보호 영역 자동 구성을 추가하지 않는다.

## 재현 명령·artifact 계획

다음은 승인 후 구현할 명령이며 현재 실행 가능한 명령이 아니다.

```bash
PYTHONPATH=src python3 -m security_tools.validation --all --output validation/v0.1
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m security_tools.gui
```

```powershell
powershell -NoProfile -File packaging/build-windows.ps1
powershell -NoProfile -File packaging/verify-windows.ps1
```

`testdata/`에 manifest·입력 Set·expected Set을 분리 보관한다.
`validation/v0.1/`에 actual·suite별 집계·오류 상세·코드 commit·dirty 상태/소스 해시·문서 버전/해시·실행 환경을 보관한다.
자체 통합·GUI·Windows 배포 검증 보고서를 공식 결과와 분리한다.
`dist/`에 EXE 또는 portable ZIP과 SHA-256을 보관한다.
`docs/PROGRESS.md`를 각 단계의 근거와 남은 작업에 맞춰 갱신한다.

## 승인 시 추가 조건

상세 SAGE 원문은 PDF 표지 버전·최종 URL·로컬 경로·SHA-256을 기록한 뒤 해당 알고리즘 구현에 사용한다.
Cip1은 TS 33.401 C.3의 CK/COUNT-C/BEARER/DIRECTION/LENGTH 및 bit 순서 대응을 문서화하고 검증한다.
manifest·입력·expected 파일을 Git으로 추적한다.
Markdown의 중첩 링크와 깨진 로컬 링크를 검사하고 수정한다.

## CONTRACT CHANGE — 상세 원문 버전 확인 (2026-11-01)

TS 35.221 wrapper는 SAGE v1.7을 참조하지만 확보한 공식 GSMA Document 1 표지는 v1.8 (2019-01-24)이다.
변경 이력은 integrity 최대 입력 길이 증가를 명시한다.
ZUC 구현 전 이 사실을 기록하며 실제 확보한 v1.8을 구현 명세로 고정한다.
공식 테스트 Document 3 v1.1, 필수 36건과 비교 의미는 유지한다.
이는 실제 표지 버전을 기록하고 재승인 대기 없이 진행하라는 사용자 지시를 적용한 출처 갱신이다.
