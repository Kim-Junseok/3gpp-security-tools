# 3GPP Security Tools

Windows GUI에서 LTE/NR legacy Ciphering·Integrity 0~3을 계산한다.
송신·수신 탭에서 두 기능의 사용 여부와 알고리즘을 각각 선택한다.
GUI와 공식 테스트 실행기는 동일한 Pure Python 코어를 사용한다.

문서 profile: README_DOC. 이 버전은 검증 결과와 남은 항목을 공개하는 연구용 배포 후보이다.

## 실행

[Windows 배포 후보 다운로드](https://github.com/Kim-Junseok/3gpp-security-tools/releases/tag/v0.1.0-rc2)에서 ZIP을 받아 압축을 푼다.


배포 폴더의 `3GPP-Security-Tools.exe`를 실행한다.
사용자 환경에는 Python·pip·외부 라이브러리 설치가 필요 없다.
단일 EXE에 CPython, Tcl/Tk, 계산 코어와 공식 검증 데이터를 포함한다.
배포 ZIP의 `licenses/`에 포함 런타임의 라이선스 문서를 제공한다.
해당 문서는 저장소의 [packaging/licenses/](packaging/licenses/)에서도 확인할 수 있다.
다른 작업 폴더에서 실행할 수 있다.
서버 연결이나 계정 로그인이 필요하지 않다.

실제 검증한 Windows 버전과 배포 파일 SHA-256은 [검증 기록](docs/VALIDATION.md)에 기록한다.
Windows 10·ARM64와 새로 설치한 Windows VM은 검증 환경에 포함하지 않는다.

## 사용법

1. 송신 또는 수신 탭을 선택한다. 탭은 무선 UL/DL DIRECTION을 반전하지 않는다.
2. Ciphering·Integrity를 각각 켜고 알고리즘 번호를 선택한다.
3. 활성화된 키와 COUNT·BEARER·DIRECTION을 입력한다. COUNT는 Decimal(기본)·Hex·Bit 중 입력 형식을 선택한다.
4. 데이터 형식을 Hex 또는 Bit로 선택하고 데이터를 입력한다. 길이는 자동 계산한다.
5. 현재 연산이 표시된 실행 버튼을 누른다. 결과와 bit 길이를 확인하고 복사한다.

| 선택 | 송신 | 수신 |
|---|---|---|
| Ciphering만 | 암호화 | 복호화 |
| Integrity만 | MAC-I 생성; 원본은 별도 표시 | 별도 수신 MAC-I와 비교 |
| 둘 다 | MAC-I 생성 → bit 단위 연결 → 전체 암호화 | 전체 복호화 → 마지막 32-bit 분리 → MAC 검증 |
| 둘 다 해제 | 실행 비활성화 | 실행 비활성화 |

각 기능의 ‘사용 안 함’은 단계를 생략한다.
알고리즘 0은 Null 정의를 적용한다.
Cip0는 입력을 보존하고 Itg0는 `00000000` MAC-I를 생성한다.
Itg0의 비교 결과는 인증 성공을 뜻하지 않는다.
표준의 Null 수신 처리는 MAC 인증 검사를 수행하지 않는다.
Core의 `matches`는 도구의 진단용 값 동등성이고 `authentication`은 항상 `unprotected`이다.

| 번호 | Ciphering LTE / NR | Integrity LTE / NR | 기반 |
|---|---|---|---|
| 0 | EEA0 / NEA0 | EIA0 / NIA0 | Null |
| 1 | 128-EEA1 / 128-NEA1 | 128-EIA1 / 128-NIA1 | SNOW 3G |
| 2 | 128-EEA2 / 128-NEA2 | 128-EIA2 / 128-NIA2 | AES |
| 3 | 128-EEA3 / 128-NEA3 | 128-EIA3 / 128-NIA3 | ZUC |

COUNT는 **Decimal(기본)·Hex·Bit**를 지원하며 범위는 0~4,294,967,295이다.
선택한 형식으로 입력값을 해석한다. BEARER는 **10진수 0~31**이다.
DIRECTION은 0=UL, 1=DL이다.
비Null 키는 각각 정확히 128-bit여야 한다.
결합 처리의 K_enc와 K_int는 독립 입력이다.
두 계산에는 공통 COUNT·BEARER·DIRECTION을 적용한다.
송신·수신 탭은 기능 사용 여부·알고리즘·키와 키 형식·COUNT와 COUNT 형식·BEARER·DIRECTION 설정을 공유한다.
데이터와 수신 MAC-I, 결과 표시 형식은 각 탭에서 따로 유지한다.

Hex 입력은 공백·탭·줄바꿈을 제외한 짝수 개 digit를 byte로 해석한다.
Bit 입력은 공백을 제외한 0·1 개수로 길이를 계산한다.
GUI의 Hex 출력·복사·Bit→Hex 변환은 `00 01 AB CD`처럼 대문자와 byte 사이 공백을 사용한다.
Hex→Bit 변환은 각 byte를 8-bit로 표시해 선행 0을 보존한다.
Bit→Hex는 유효 길이가 8의 배수일 때만 허용한다.
비정렬 결과는 정확한 Bit 문자열로 표시·복사한다.
예를 들어 `00 01`은 16-bit이며, `00010100101`은 11-bit이다.
11-bit 결합 송신 결과는 43-bit이다.

결합 수신이 MAC 검증에 실패하면 복호화 출력을 **검증 실패 데이터**로 표시한다.
전체 입력이 32-bit 미만인 결합 수신은 입력 오류이다.
Null 외 SNOW 3G/ZUC integrity 입력은 명세에 따라 1~2^32 bit 범위이다.

## 개발·공식 검증

WSL/Linux의 Python 3.12.3 또는 Windows Python 3.12에서 실행할 수 있다.
코어·공식 실행기·자체 통합 테스트에는 외부 Python 패키지가 필요 없다.
소스 GUI 실행에는 개발 Python의 Tkinter/Tcl/Tk가 필요하다.

```bash
PYTHONPATH=src python3 -m security_tools.validation --all --output validation/v0.1/linux
PYTHONPATH=src python3 tools/run_tests.py --output validation/v0.1/integration-report.json
PYTHONPATH=src python3 -m security_tools.gui
```

특정 suite는 `--suite Cip2 --suite Itg2`처럼 지정한다.
공식 expected는 원문 전사 파일이며 실행 중 생성하거나 갱신하지 않는다.
알고리즘 정확성은 계산 결과를 공식 테스트의 기대값과 비교해 검증한다.
공식 실행기는 원문의 LENGTH를 읽는다.
사용자 Hex 입력의 자동 byte 길이 규칙을 공식 벡터에 적용하지 않는다.
마지막 byte/word의 유효 길이 이후 하위 bit만 비교에서 제외한다.

| Suite | 필수 수 | 고정 출처 |
|---|---:|---|
| Cip1 | 5 | TS 35.217 v19.0.0 → SAGE Document 3 v1.1 (2012-10-25), §4 |
| Itg1 | 7 | TS 33.401 v19.2.0 C.4 |
| Cip2 | 6 | TS 33.401 v19.2.0 C.1 |
| Itg2 | 8 | TS 33.401 v19.2.0 C.2 |
| Cip3 | 5 | TS 35.223 v19.0.0 → SAGE Document 3 v1.1 (2011-01-04), §4 |
| Itg3 | 5 | 위 SAGE Document 3 §5 |
| 합계 | **36** | 요구사항에 지정된 알고리즘 입출력 suite |

Null 동작, 통합·경계 테스트, 실제 GUI widget 테스트, Windows 배포 검증은 별도 집계한다.
원문 링크·표지 버전·해시와 Cip1 매핑·입력 정규화는 [SOURCES.md](docs/SOURCES.md)를 참조한다.
SNOW/ZUC primitive 내부 상태 테스트나 다른 문서 전체의 conformance 검증을 36건에 포함했다고 해석하지 않는다.

## Windows 빌드

Windows Python 3.12 x64와 Tcl/Tk를 사용하는 개발 환경에서 실행한다.
개발 의존성 설치는 배포 사용자에게 요구하는 설치가 아니다.
실제 사용한 환경은 CPython 3.12.10 x64, Tcl/Tk 8.6, PyInstaller 6.22.3이다.

```powershell
& C:\Python312\python.exe -m pip install -r packaging/requirements-windows.txt
powershell -NoProfile -File packaging/build-windows.ps1 -Python C:\Python312\python.exe
powershell -NoProfile -File packaging/verify-windows.ps1
```

프로젝트 내부 `.build/windows-python/python.exe`가 있으면 `-Python`을 생략한다.
이번 작업은 공식 full ZIP 런타임을 그 경로에 압축 해제해 사용했다.
WSL/Linux에서 PyInstaller를 실행한 산출물을 Windows EXE로 사용하지 않는다.
빌드 입력 commit·파일 해시는 EXE 내부 `build-info.json`에 포함된다.
Windows Git이 없으면 빌드 전에 WSL에서 `python3 tools/stamp_source.py`를 실행한다.

패키징된 코어로 공식 검증을 실행하는 개발용 경로도 제공한다.

```powershell
$p = Start-Process .\dist\3GPP-Security-Tools.exe -ArgumentList '--validate --output C:\Temp\3gpp-validation' -Wait -PassThru
$p.ExitCode
```

종료 코드 0은 선택한 공식 suite 전부 PASS, 1은 불일치·실행 실패를 뜻한다.
검증 산출물은 `answers.json`과 `official-report.json`이다.
GUI 시험은 `--gui-smoke-report C:\Temp\gui-report.json`으로 별도 실행한다.

## Python API

```python
from security_tools.bits import Bits, from_result
from security_tools.core import transmit, receive

options = dict(ciphering=2, integrity=2,
               enc_key=bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
               int_key=bytes.fromhex("f0e0d0c0b0a090807060504030201000"),
               count=0x12345678, bearer=17, direction=1)
sent = transmit(Bits.parse("00010100101", "Bit"), **options)
received = receive(from_result(sent["data"]), **options)
assert received["data"]["bits"] == "00010100101"
assert received["authentication"] == "passed"
```

`transmit`·`receive`·`verify` 결과는 JSON 직렬화 가능한 dictionary이다.
개별 primitive `cipher`·`mac`은 buffer와 유효 길이를 가진 `Bits`를 반환한다.
`Bits.to_dict()`로 동일한 공개 표시 형식으로 변환한다.
`data.hex`는 비정렬 데이터에서 `null`이며 `data.bits`와 `data.bit_length`를 사용한다.

## 저장소와 제한

- `src/`: 계산 코어·GUI·공식 테스트 실행기
- `tests/`: 통합·경계값 테스트
- `testdata/`: 공식 테스트 목록·입력값·기대값
- `validation/`: 계산 결과·검증 보고서
- `packaging/`: Windows 빌드·배포 검증 스크립트
- `tools/`: 데이터 전사·배포물 생성 도구
- `docs/`: 출처·검증 결과·릴리스 기록·후속 계획

이 도구는 입력 데이터 전체를 MAC 대상으로 삼고, 결합 처리에서는 Data || MAC-I 전체를 ciphering 대상으로 삼는다.
실제 NAS/PDCP PDU를 파싱하거나 PDCP/SDAP header의 보호 영역을 자동 구성하지 않는다.
256-bit NEA/NIA는 [후속 목록](docs/FOLLOW_UP.md)이며 AEAD/NCA는 제외한다.
