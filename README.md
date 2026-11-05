# 3GPP Security Tools

Windows GUI에서 legacy Ciphering·Integrity 0~3과 256-bit NEA/NIA 4~6을 계산한다.
GUI는 영문이며, 사용법과 검증 문서는 한글로 제공한다.
GUI와 공식 테스트 실행기는 동일한 Python 계산 코어를 사용한다.

## 실행

[최신 배포 후보 v0.1.0-rc4](https://github.com/Kim-Junseok/3gpp-security-tools/releases/tag/v0.1.0-rc4)에서 Windows ZIP을 받아 압축을 푼다.
`3GPP-Security-Tools.exe`를 실행한다. Python이나 별도 라이브러리를 설치할 필요가 없다.
단일 EXE에 CPython·Tcl/Tk·계산 코어·공식 검증 데이터를 포함한다.
배포 ZIP의 `RUNNING.txt`는 영문 실행 안내이며, `README.md`와 `docs/`는 한글 문서다.
런타임 이용 조건은 배포 ZIP의 `licenses/`와 저장소의 [packaging/licenses/](https://github.com/Kim-Junseok/3gpp-security-tools/tree/main/packaging/licenses)에서 확인할 수 있다.

## 사용법

1. `Transmit`(송신) 또는 `Receive`(수신) 탭을 선택한다.
2. `Enable Ciphering`·`Enable Integrity`에서 기능 사용 여부와 알고리즘을 각각 선택한다.
3. 활성화된 키와 COUNT·BEARER·DIRECTION을 입력한다.
4. 알고리즘 4~6을 사용하면 EXTRA_IV를 입력한다. Integrity 4~6에서는 MAC-I 길이도 선택한다.
5. 입력 데이터 형식을 Hex 또는 Bit로 선택하고 데이터를 입력한다. 길이는 자동 계산한다.
6. 실행 버튼을 누르고 결과를 확인한다. `Copy result`로 결과를 복사한다.

| 기능 선택 | 송신 | 수신 |
|---|---|---|
| Ciphering만 | 암호화 | 복호화 |
| Integrity만 | MAC-I 생성 | 원본 데이터와 별도 수신 MAC-I 검증 |
| 두 기능 모두 | MAC-I 생성 → 데이터 뒤에 추가 → 전체 암호화 | 전체 복호화 → MAC-I 분리 → 검증 |
| 두 기능 해제 | 실행 비활성화 | 실행 비활성화 |

| 번호 | Ciphering | Integrity | 키 길이 | 기반 |
|---|---|---|---:|---|
| 0 | EEA0 / NEA0 | EIA0 / NIA0 | 불필요 | Null |
| 1 | 128-EEA1 / 128-NEA1 | 128-EIA1 / 128-NIA1 | 128 bit | SNOW 3G |
| 2 | 128-EEA2 / 128-NEA2 | 128-EIA2 / 128-NIA2 | 128 bit | AES |
| 3 | 128-EEA3 / 128-NEA3 | 128-EIA3 / 128-NIA3 | 128 bit | ZUC |
| 4 | 256-NEA4 | 256-NIA4 | 256 bit | SNOW 5G |
| 5 | 256-NEA5 | 256-NIA5 | 256 bit | AES |
| 6 | 256-NEA6 | 256-NIA6 | 256 bit | ZUC |

- **키:** K_enc와 K_int는 독립 입력이다. 128-bit 키는 16 byte, 256-bit 키는 32 byte다. Hex 공백·붙여쓰기를 모두 허용한다.
- **COUNT:** Decimal(기본)·Hex·Bit를 지원한다. 범위는 0~4,294,967,295이며 선택한 형식으로 입력값을 해석한다.
- **BEARER:** 10진수 0~31이다.
- **DIRECTION:** 0=UL, 1=DL이다. 탭을 바꿔도 값이 반전되지 않는다.
- **EXTRA_IV:** 알고리즘 4~6에 적용하는 48-bit 값이다. 기본값은 6-byte 0이다.
- **MAC-I 길이:** Integrity 0~3은 4 byte로 고정한다. Integrity 4~6은 4~16 byte를 선택한다.

송신·수신 탭은 기능 사용 여부·알고리즘·키와 형식·COUNT와 형식·BEARER·DIRECTION·EXTRA_IV·MAC 길이를 공유한다.
입력 데이터·수신 MAC-I·결과 표시 형식은 탭마다 따로 유지한다.
작은 창에서는 오른쪽 스크롤바로 나머지 입력과 결과를 확인한다.

## 입력·결과 형식

Hex 입력은 공백·탭·줄바꿈을 제외한 짝수 개 digit를 byte로 해석한다.
Bit 입력은 공백을 제외한 0·1 개수로 길이를 계산한다.
GUI의 Hex 출력·복사·Bit→Hex 변환은 `00 01 AB CD`처럼 대문자와 byte 사이 공백을 사용한다.
Hex→Bit 변환은 선행 0을 보존한다. Bit→Hex 변환은 유효 길이가 8의 배수일 때만 허용한다.
비정렬 결과는 Bit 문자열로 표시하며 padding을 추가하지 않는다.

결합 송신의 출력 길이는 데이터 길이 + MAC 길이다.
예를 들어 11-bit 데이터에 4-byte MAC을 붙이면 43 bit, 8-byte MAC을 붙이면 75 bit다.
결합 수신에서는 선택한 MAC 길이만큼 끝부분을 분리한다.
MAC 검증 실패 시 출력은 `Data failed authentication`으로 표시한다.

기능을 끄면 해당 단계를 생략한다. 알고리즘 0은 Null 연산이다.
Null Ciphering은 데이터를 보존하고 Null Integrity는 `00 00 00 00`을 생성한다.
Null의 MAC 값 비교는 인증 성공을 뜻하지 않으며 상태는 `unprotected`다.

## 개발·검증

계산 코어와 공식·통합 테스트에는 외부 Python 패키지가 필요 없다.
소스 GUI 실행에는 Tkinter·Tcl/Tk가 필요하다.

```bash
PYTHONPATH=src python3 -m security_tools.validation --all --output validation/local/linux
PYTHONPATH=src python3 tools/run_tests.py --output validation/local/integration-report.json
PYTHONPATH=src python3 -m security_tools.gui
```

특정 suite는 `--suite Cip2 --suite NEA5 --suite NIA5`처럼 선택한다.
공식 기대값은 추적 중인 원문 전사 파일이며 계산 결과로 생성하지 않는다.
공식 실행기는 원문의 유효 bit 길이를 보존한다.

| 검증 구분 | 케이스 수 |
|---|---:|
| Legacy 알고리즘 입출력 | 36 |
| 256-bit NEA/NIA 입출력 | 72 |
| Release 20 primitive | 27 |
| 공식 벡터 합계 | **135** |

내부 상태 snapshot 63건은 primitive 케이스 안의 하위 검사이며 합계에 더하지 않는다.
자체 통합 테스트와 GUI 검사는 공식 벡터와 별도로 집계한다.
원문 버전·해시는 [SOURCES.md](docs/SOURCES.md), 환경별 결과와 배포 EXE 해시는 [VALIDATION.md](docs/VALIDATION.md)에 기록한다.

## Windows 빌드

Windows Python 3.12 x64와 Tcl/Tk를 사용하는 개발 환경에서 실행한다.
PyInstaller와 빌드 의존성은 `packaging/requirements-windows.txt`로 고정한다.

```powershell
& C:\Python312\python.exe -m pip install -r packaging/requirements-windows.txt
powershell -NoProfile -File packaging/build-windows.ps1 -Python C:\Python312\python.exe
powershell -NoProfile -File packaging/verify-windows.ps1 -ReportDirectory validation/local/windows
```

공식 테스트는 135건, Windows GUI 검사는 199건을 기준으로 확인한다.
프로젝트의 개발용 `.build/windows-python/python.exe`가 있으면 `-Python`을 생략할 수 있다.
Windows Git이 없으면 빌드 전에 WSL에서 `python3 tools/stamp_source.py`를 실행한다.
EXE에는 빌드 입력 commit과 파일 해시를 포함한다.

패키징된 EXE의 공식·GUI 검사는 다음처럼 실행한다.

```powershell
$p = Start-Process .\dist\3GPP-Security-Tools.exe -ArgumentList '--validate --output C:\Temp\3gpp-validation' -Wait -PassThru
$p.ExitCode
$p = Start-Process .\dist\3GPP-Security-Tools.exe -ArgumentList '--gui-smoke-report C:\Temp\3gpp-gui.json' -Wait -PassThru
$p.ExitCode
```

릴리스 ZIP과 소스 ZIP은 Git이 있는 개발 환경에서 생성한다.
검증 보고서의 EXE 해시가 실제 파일과 일치해야 하며 문서·검증 기록을 먼저 커밋한다.

```bash
python3 tools/package_release.py --tag v0.1.0-rc4 --evidence validation/rc4/windows
```

## Python API

```python
from security_tools.bits import Bits, from_result
from security_tools.core import transmit, receive

options = dict(ciphering=5, integrity=5,
               enc_key=bytes(range(32)), int_key=bytes(range(32, 64)),
               count=123456789, bearer=17, direction=1,
               extra_iv=bytes(6), mac_bytes=8)
sent = transmit(Bits.parse("00 01 AB CD"), **options)
received = receive(from_result(sent["data"]), **options)
assert received["data"]["hex"] == "0001abcd"
assert received["authentication"] == "passed"
```

`transmit`·`receive`·`verify`는 dictionary, `cipher`·`mac`은 `Bits`를 반환한다.
`Bits.to_dict()`로 직렬화할 수 있다. Core JSON의 Hex는 공백 없는 소문자이며 GUI 표시와 구분한다.
비정렬 결과의 `hex`는 `null`이고 `bits`와 `bit_length`를 사용한다.

## 폴더·범위

- `src/`: 계산 코어·GUI·공식 테스트 실행기
- `tests/`: 통합·경계값 테스트
- `testdata/`: 공식 테스트 목록·입력값·기대값
- `validation/`: 계산 결과·검증 보고서
- `packaging/`: Windows 빌드·배포 검증 스크립트
- `tools/`: 데이터 전사·배포물 생성 도구
- `docs/`: 출처·검증 결과·릴리스 기록·후속 계획

입력 데이터 전체를 MAC 대상으로 삼고 결합 처리에서는 Data || MAC-I 전체를 암호화한다.
이 도구의 결합 처리는 표준 NCA 기능이 아니다.
AEAD/NCA와 NAS/PDCP PDU 파싱·보호 영역 자동 구성은 범위에서 제외한다.
남은 검증은 [FOLLOW_UP.md](docs/FOLLOW_UP.md)에 기록한다.
