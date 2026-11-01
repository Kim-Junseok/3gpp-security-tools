# 구현 진행 기록

- 기준일: 2026-11-01 (Asia/Seoul)
- 문서 profile: TECHNICAL_NOTE
- 전체 상태: 구현 진행 중. 사용자 계약 승인 수신. AES 공식 14/14 PASS; 전체/GUI/배포 검증 미완료.

| 단계 | 상태 | 근거 / 다음 작업 |
|---|---|---|
| 요구사항·작업 지침 확인 | DONE | 요구사항 전체와 canonical writing guide 읽음. 구현 전 검토 gate 확인. |
| 기존 저장소·baseline 조사 | DONE | 홈은 Git 작업 트리가 아님. 전용 로컬 저장소 및 연결 GitHub 검색에서 대상 미발견. 새 로컬 경로 제안. |
| 공식 버전·case 목록 조사 | PARTIAL | ETSI 버전 목록·wrapper 및 GSMA SAGE 테스트 원문 확인. 지정 suite 총 36건. expected 전체 전사·대조 미실시. |
| 공식 원문 로컬 확보 | PARTIAL | 3개 PDF 및 pdftotext 캐시 확보. URL·해시는 SOURCES.md 참조. 상세 알고리즘 원문 추가 확보 필요. |
| Windows 환경 조사 | DONE | Windows 11 Home x64, 버전 10.0.26200. 일반 interop 실패, 읽기 전용 escalation 성공. 실제 Python 설치 미확인. |
| TASK CONTRACT 검토 | DONE | 2026-11-01 사용자 승인 및 추가 조건 반영. |
| Cip2/Itg2·공식 14건·최소 GUI | IN PROGRESS | AES 공식 14/14 PASS. GUI 작성, Windows 패키징 준비. |
| 초기 Windows EXE 빌드·실행 | NOT STARTED | 최소 GUI 직후 수행. |
| 나머지 legacy·공식 전체 | NOT STARTED | 필수 목록 36건을 분모로 사용. |
| 결합 송신·수신·전체 GUI | NOT STARTED | 16개 조합, 정렬/비정렬과 변조 검증. |
| 최종 검증·README·배포물 | NOT STARTED | 공식·통합·GUI·Windows 결과 분리. |

## 현재 검증 결과

공식 알고리즘 실행 0건, 자체 통합 테스트 0건, GUI 실행 테스트 0건, Windows EXE 테스트 0건이다.
버전 조회와 원문 목록 확인은 알고리즘/배포 검증으로 집계하지 않는다.
현재 실행·빌드 가능한 프로그램 또는 EXE는 없다.

## 환경 관찰

WSL2 Ubuntu-24.04, Linux x86_64, Python 3.12.3을 확인했다.
WSL Python에서 tkinter, pytest, PyInstaller 모듈을 찾지 못했다.
pdftotext와 git, gh는 명령 경로에 존재한다.
Windows `python`/`python3` 명령은 WindowsApps 경로에 있으며 정상 Python 런타임의 존재를 뜻하지 않는다.
기본 네트워크에서는 ETSI DNS 조회가 실패했지만 escalation으로 PDF 세 개를 확보했다.

## 다음 결정

[TASK_CONTRACT.md](TASK_CONTRACT.md)의 사용자 검토가 필요하다.
승인 후 구현→공식 검증→최소 GUI→초기 Windows 패키징 순서로 진행한다.
실행 환경이나 자료에 문제가 생기면 영향받는 항목과 독립적으로 진행할 수 있는 항목을 구분한다.

## 구현 중 기록

- manifest·입력·expected 파일을 Git index에 등록했다. importer는 계산 코어를 import하지 않는다.
- Cip1-005 원문 14쪽의 `60876A0`를 32-bit word `060876A0`로 정규화했다. 같은 원문 row 18의 `AE56E26E XOR A85E94CE`로 확인했다.
- Windows CPython 3.12.10 공식 full ZIP을 `.build/windows-python`에 풀었다. Tcl/Tk 8.6 import 성공. 시스템 설치는 수행하지 않았다.
- CONTRACT CHANGE (출처 확보): wrapper의 SAGE EEA3/EIA3 v1.7 원문은 찾지 못했고, 공식 GSMA 파일의 표지는 v1.8 (2019-01-24)이다. 변경 이력은 integrity 최대 입력 길이 증가를 명시한다. 아직 ZUC 구현을 시작하지 않았다. 고정 테스트 Document 3 v1.1과 36건·비교 기준은 유지한다. 사용자 지시의 실제 표지 버전 기록 및 재승인 없이 진행 조건에 따라 확보한 v1.8을 상세 구현 명세로 기록해 사용한다.
