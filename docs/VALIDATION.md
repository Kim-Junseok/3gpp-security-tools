# 검증 기록

- 문서 profile: TECHNICAL_NOTE
- 실행일: 2026-11-01 (Asia/Seoul)
- 상태: 로컬 Windows 배포 후보 검증 완료. 공개 Release 후보 게시 준비. 새 Windows VM 검증은 미완료.

## 공식 알고리즘 결과

원문에서 전사한 expected Set을 읽고 동일 Core의 actual과 비교했다.
필수 분모는 실행 전에 고정한 36건이다.
마지막 buffer의 LENGTH 이후 하위 bit만 비교에서 제외했다.

| Suite | 고정 출처 | 필수 | Linux PASS | Windows EXE PASS | FAIL / ERROR / SKIP / BLOCKED |
|---|---|---:|---:|---:|---|
| Cip1 | TS 35.217 19.0.0 → SAGE Doc3 1.1 §4 | 5 | 5 | 5 | 0 / 0 / 0 / 0 |
| Itg1 | TS 33.401 19.2.0 C.4 | 7 | 7 | 7 | 0 / 0 / 0 / 0 |
| Cip2 | TS 33.401 19.2.0 C.1 | 6 | 6 | 6 | 0 / 0 / 0 / 0 |
| Itg2 | TS 33.401 19.2.0 C.2 | 8 | 8 | 8 | 0 / 0 / 0 / 0 |
| Cip3 | TS 35.223 19.0.0 → SAGE Doc3 1.1 §4 | 5 | 5 | 5 | 0 / 0 / 0 / 0 |
| Itg3 | 위 SAGE Doc3 1.1 §5 | 5 | 5 | 5 | 0 / 0 / 0 / 0 |
| 합계 | 지정된 legacy 알고리즘 입출력 suite | **36** | **36** | **36** | **0 / 0 / 0 / 0** |

이 결과는 지정된 공식 벡터와의 일치이다.
SNOW/ZUC 내부 상태 자료 전체나 다른 문서의 conformance 자료 전체를 검증했다는 뜻은 아니다.
Null은 고정 문서의 정의 기반 자체 시험이며 공식 36건에 포함하지 않는다.

## 자체 통합·경계 검증

[통합 보고서](../validation/v0.1/integration-report.json): unittest test method **21개 PASS**, failure/error/skip 0.
16개 Ciphering/Integrity 조합 × 정렬/비정렬 입력 = 32개 참조 연결·왕복 subcase를 확인했다.
참조 조립은 production transmit/receive/concat/split을 호출하지 않는 bit 문자열 연산을 사용했다.
개별 cipher/MAC primitive는 공식 벡터 검증을 통과한 함수를 호출했다.
비Null integrity 12조합 × 2정렬 × 데이터/MAC 변조 = 48개 변조 subcase에서 실패 상태를 확인했다.
선행 0, key 길이, 숫자 범위, Null/단계 생략 차이, 32-bit 미만 결합 수신 오류, 고정 분모 누락 검출도 확인했다.
위 subcase는 test method 수와 중복해 합산하지 않는다.
왕복 시험만으로 알고리즘 정확성을 판정하지 않았다.

## GUI 검증

[실제 Windows widget 보고서](../validation/v0.1/windows/gui-report.json): **30/30 PASS**.
송신/수신의 세 보호 조합, 필드 활성화, 두 기능 해제, Hex/Bit 변환·복사, Null, 검증 실패 표시, 짧은 수신과 홀수 Hex 오류를 확인했다.
비정렬 공식 Cip2-001과 Itg2-001도 GUI 입력 경로로 실행했다.
이 수는 공식 알고리즘 분모와 별도이다.
[실제 창 캡처](../validation/v0.1/gui-preview.png)에서 탭·필드·비정렬 43-bit 출력·MAC-I 표시를 확인했다.
캡처는 동일 GUI 소스를 Windows CPython으로 연 창이다.
배포 EXE의 widget 동작은 별도 smoke 실행으로 검증했다.

## Windows 배포 시험

실제 환경은 Windows 11 Home x64, OS 10.0.26200이다.
빌드 런타임은 CPython 3.12.10 x64, Tcl/Tk 8.6, PyInstaller 6.22.3이다.
EXE 한 개를 Windows 임시 폴더로 복사했다.
다른 작업 디렉터리에서 실행했다.
프로젝트 개발용 Python 디렉터리를 원래 경로에서 격리하고 PATH와 Python/Tcl/Tk 환경변수를 제거했다.
공식 36건과 GUI widget 30건을 그 EXE로 다시 실행했다.
Tcl/Tk의 로딩 경로는 EXE가 추출한 `_MEI.../_tcl_data`, `_tk_data`로 확인했다.
[배포 보고서](../validation/v0.1/windows/deployment-report.json)에 실제 EXE 경로·작업 폴더·환경·해시를 기록했다.

WSL 공유 경로의 개발 폴더를 Windows에서 복원할 때 파일 이동 오류가 발생했다.
이를 Linux의 이름 변경으로 복원했다.
검증 스크립트는 외부에서 격리한 런타임을 그대로 시험하도록 수정했다.
마지막 실행은 종료 코드 0이며 개발 런타임도 복원됐다.
이 오류는 GUI/공식 알고리즘 불일치가 아니며 최종 검증의 실패로 숨기지 않았다.

이 시험은 기존 Windows 호스트의 통제된 의존성 격리 시험이다.
새로 설치한 Windows VM, WSL·개발 도구가 설치된 적 없는 PC, Windows 10 및 ARM64에서는 시험하지 않았다.
따라서 해당 환경에 대한 배포 검증 완료를 표시하지 않는다.

## 재현과 provenance

배포 EXE SHA-256: `b27b536b216e8f43c6c390d27262ec6f091a4a51b9c5a6340c8148e3802f4522`.

빌드 기준 commit: `a572e34fc68b6717f2baaf1da6bfac81b6a08fb9`.
빌드 당시 문서 변경과 보고서가 있어 dirty=true로 기록했다.
EXE에 포함한 src·testdata 각 파일의 SHA-256을 [build-info.json](../validation/v0.1/build-info.json)에 보존했다.
현재 소스의 해당 계산·GUI·데이터 파일과 모두 일치함을 확인했다.
빌드 후 수정한 Windows 검증 harness의 폴더 관리 코드는 EXE의 계산 코드를 변경하지 않는다.

[Linux 공식 보고서](../validation/v0.1/linux/official-report.json), [Linux Answer Set](../validation/v0.1/linux/answers.json),
[Windows 공식 보고서](../validation/v0.1/windows/official-report.json), [Windows Answer Set](../validation/v0.1/windows/answers.json)을 분리 보관한다.
코드·문서 버전·데이터 해시·실행 환경은 각 보고서에 포함한다.
명령은 [README](../README.md)의 개발·Windows 빌드 항목을 따른다.
원문과 Cip1 정규화 근거는 [SOURCES.md](SOURCES.md)를 따른다.

## 남은 항목

- 알고리즘 사용 조건의 법적 적용 범위는 이 검증에서 판단하지 않았다. 공개 범위와 출처 안내는 DISTRIBUTION.md에 기록했다.
- 새 Windows 환경에서 Python·WSL·개발 도구 없는 상태의 시험.
- Windows 10·ARM64는 지원 검증 범위 밖이다.
- 256-bit NEA/NIA는 후속이며 AEAD/NCA는 제외한다.
