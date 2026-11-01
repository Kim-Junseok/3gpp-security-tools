# 구현 진행 기록

- 기준일: 2026-11-01 (Asia/Seoul)
- 문서 profile: TECHNICAL_NOTE
- 상태: legacy GUI·단일 Windows EXE 로컬 배포 후보 준비. 공개 저장소·Release 후보 게시 준비. 새 Windows 환경 시험은 남음.

| 단계 | 상태 | 근거 |
|---|---|---|
| 요구사항·preflight·계약 검토 | DONE | 사용자 승인과 추가 조건 반영. |
| 표준·SAGE 실제 버전·출처 확보 | DONE | 표지·최종 URL·로컬 경로·SHA-256 기록. EEA3/EIA3 v1.8 출처 갱신을 CONTRACT CHANGE로 기록. |
| manifest·입력·expected Git 추적 | DONE | testdata 세 JSON 추적. expected는 Core 출력과 분리. |
| 공통 bit·AES·최소 GUI | DONE | AES 공식 14/14, 초기 Windows EXE GUI 15/15. |
| 초기 Windows 패키징 | DONE | 실제 Windows 단일 EXE 빌드·실행과 Tcl/Tk 포함 확인. |
| legacy 0~3·공식 전체 | DONE | Linux 및 최종 Windows EXE 각각 공식 36/36. Null 별도 정의 기반 시험. |
| 결합 송신·수신·전체 GUI | DONE | 자체 21 test method, 16조합 × 2정렬 연결·왕복, 변조 48 subcase, GUI widget 30/30. |
| Windows 통제된 격리 실행 | DONE | EXE만 복사, 다른 CWD, 개발 런타임·환경변수 배제. 공식 36/36, GUI 30/30. |
| 문서·README·로컬 배포물 | DONE | 검증 결과·원문·API·실행·빌드·제약 기록. EXE/ZIP/checksum 준비. |
| 새 Windows PC/VM 시험 | NOT VERIFIED | Python·WSL·개발 도구를 설치한 적 없는 환경 미확보. 해당 VM에서 동일 verify 스크립트 실행 필요. |
| 공개 GitHub 저장소·Release | IN PROGRESS | 독립 작성 코드·벡터·EXE를 연구용 후보로 준비. 원문 PDF와 참조 C 코드 전체 제외. |

## 근거와 제한

[SOURCES.md](SOURCES.md)에 실제 PDF 버전과 해시·Cip1 매핑을 기록했다.
Cip1-005의 원문 32-bit word `60876A0`는 같은 원문의 keystream/enc-dec 표에 따라 `060876A0`로 정규화했다.
구현의 출력으로 expected를 생성하지 않았다.
공식·통합·GUI·배포 결과는 [VALIDATION.md](VALIDATION.md)와 별도 JSON에 기록했다.

Windows 빌드 중 GUI 오류 검사를 추가한 뒤 진행 중인 빌드를 중단하고 소스를 다시 고정해 빌드했다.
개발 런타임 복원 과정의 WSL 공유 경로 오류를 해결하고 동일 EXE 시험을 재실행했다.
마지막 검증 스크립트 종료 코드는 0이며 개발 런타임은 복원됐다.

요구사항 §7의 모든 배포·공개 조건이 충족된 최종 공개 릴리스로 표시하지 않는다.
256-bit 후속 목록은 [FOLLOW_UP.md](FOLLOW_UP.md)로 분리한다.
