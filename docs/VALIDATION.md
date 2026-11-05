# 검증 기록

## v0.1.0-rc3 — 2026-11-05

기준 소스는 `c417127`이며, 클라우드 작업의 영문 GUI와 256-bit NEA/NIA 구현을 포함한다.
배포 EXE는 [Windows CI 실행](https://github.com/Kim-Junseok/3gpp-security-tools/actions/runs/41648779553)의 검증 아티팩트를 사용한다.
재빌드하지 않고 검증된 파일을 그대로 배포한다.
ZIP 아티팩트와 EXE 해시를 확인한 뒤 로컬 Windows 11에서 같은 EXE를 다시 검사했다.

### 공식 벡터

| 구분 | 필수 수 | Linux 로컬 | Windows CI EXE | Windows 11 EXE |
|---|---:|---:|---:|---:|
| Legacy 알고리즘 입출력 | 36 | 36 | 36 | 36 |
| 256-bit NEA/NIA 입출력 | 72 | 72 | 72 | 72 |
| Release 20 primitive | 27 | 27 | 27 | 27 |
| 합계 | **135** | **135** | **135** | **135** |

각 환경에서 FAIL·ERROR·SKIP·BLOCKED는 0이다.
SNOW 5G·ZUC 내부 상태 snapshot 63건은 primitive 하위 검사이며 합계에 더하지 않는다.
Null 정의와 자체 통합·GUI 검사는 공식 벡터와 별도로 집계한다.
입력·expected의 해시는 보고서에 기록하며 구현 출력으로 expected를 생성하지 않는다.

- [이번 Linux 공식 보고서](../validation/rc3/linux/official-report.json)
- [기존 Windows CI EXE 공식 보고서](../validation/256-bit/windows/official-report.json)
- [이번 Windows 11 EXE 공식 보고서](../validation/rc3/windows/official-report.json)

### 자체 통합·GUI

| 구분 | 결과 | 근거 |
|---|---:|---|
| Linux 통합·경계 테스트 | 31개 PASS | [이번 보고서](../validation/rc3/integration-report.json) |
| Linux CI GUI widget | 195/195 PASS | [클라우드 보고서](../validation/256-bit/ci-linux/gui-report.json) |
| Windows CI EXE GUI widget | 197/197 PASS | [클라우드 보고서](../validation/256-bit/windows/gui-report.json) |
| Windows 11 EXE GUI widget | 197/197 PASS | [이번 보고서](../validation/rc3/windows/gui-report.json) |

통합 검사는 키·EXTRA_IV·MAC 길이·정렬/비정렬 데이터·결합 처리·변조·범위 오류를 포함한다.
GUI 검사는 0~6 기능 선택·탭 공유·형식 변환·복사·오류 표시·가변 MAC·공식 입력과 작은 창의 스크롤을 포함한다.
Windows 전용 DPI·글꼴 검사 2건 때문에 GUI 분모가 Linux와 다르다.

### Windows 실행·DPI

CI 환경은 Windows Server 2025 x64, 로컬 재검증 환경은 Windows 11 Home x64(10.0.26200)이다.
로컬에서는 EXE 한 개를 임시 폴더에 복사하고 다른 작업 폴더에서 실행했다.
개발용 Python 경로를 일시 격리하고 PATH·Python/Tcl/Tk 환경변수를 제거한 상태에서 공식·GUI 검사를 통과했다.
개발 런타임은 검사 후 복원했다.
[배포 보고서](../validation/rc3/windows/deployment-report.json)에 격리 조건과 EXE 해시를 기록한다.

시스템 DPI 인식 상태와 192 DPI(200%) 배율을 확인했다.
[Windows 창 캡처](../validation/rc3/gui-preview.png)에서 영문 GUI·256-bit 설정·EXTRA_IV·8-byte MAC·결과·스크롤 배치를 확인했다.
캡처는 동일 소스를 Windows Python으로 실행한 창이며, 배포 EXE의 widget 동작은 별도로 검사했다.
[캡처 정보](../validation/rc3/visual-capture.json)에 실제 창 크기와 DPI를 기록한다.
서로 다른 DPI 모니터 사이 이동, 새 Windows PC/VM, Windows 10·ARM64는 검증하지 않았다.

### 빌드·원문 대조

- EXE SHA-256: `fc45b468faa1489cabc9fc74768d77e3e8ff64d73bb74b04452314cebd2129e7`
- CI 빌드 기준: `c7748f27ec7e418403a1cfd09e114ae1370ce482`
- 빌드 런타임: CPython 3.12.10 x64·PyInstaller 6.22.3.
- [기존 빌드 입력 해시](../validation/256-bit/windows/build-info.json)와 현재 파일 34개를 대조했다. Windows CRLF를 복원하면 모두 일치한다. [대조 기록](../validation/rc3/source-match.json)
- Release 20 원문 ZIP·DOCX 9개를 추적 중인 해시와 대조했다. [확보 기록](../validation/rc3/source-acquisition.json)

재현 명령은 [README](../README.md)의 개발·Windows 빌드 항목을 따른다.
클라우드에서 실행한 초기 범위와 원문 해석은 [scope.json](../validation/256-bit/scope.json)에 보관한다.

## 이전 배포 후보

| 버전 | 공식 벡터 | 통합 테스트 | Windows EXE GUI | 기록 |
|---|---:|---:|---:|---|
| rc1 | 36/36 | 21개 | 30/30 | [Windows 보고서](../validation/v0.1/windows/official-report.json) |
| rc2 | 36/36 | 24개 | 44/44 | [Windows 보고서](../validation/gui-update/windows/official-report.json) |

이전 후보의 파일·태그·검증 기록은 보존한다. GitHub 릴리스 제목과 본문은 영어로 제공한다.
