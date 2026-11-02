# 릴리스 기록

## v0.1.0-rc2 — GUI 표시·입력 개선

- Windows 시스템 DPI 인식을 선언하고 한글 UI에 맑은 고딕을 적용했다. 200% 배율에서 실제 창을 확인했다.
- GUI의 Hex 출력·복사·Bit→Hex 변환을 `00 01 AB CD` 형식으로 통일했다.
- COUNT에 Decimal(기본)·Hex·Bit 입력을 추가했다.
- 송신·수신 탭이 사용 여부·알고리즘·키·COUNT·BEARER·DIRECTION 설정을 공유한다. 데이터는 탭마다 유지한다.

공식 테스트는 Linux와 Windows EXE에서 각각 36/36 PASS다.
자체 통합·경계 테스트는 24개, Windows EXE GUI 검사는 44/44 PASS다.
개발 런타임을 격리한 상태에서도 EXE의 공식·GUI 검사를 통과했다.
EXE SHA-256: `423a9b5b7f4c82c58e7e063520b221c326fa785f5e77168ef9bda861ff6f2a56`.

배포 ZIP의 EXE를 실행한다. Python이나 별도 라이브러리 설치는 필요 없다.
새 Windows PC/VM, Windows 10·ARM64 검증은 미완료다.
세부 결과는 [VALIDATION.md](VALIDATION.md)에 기록한다.

## v0.1.0-rc1 — Windows GUI 배포 후보

송신/수신 탭에서 legacy 0~3 Ciphering·Integrity를 독립적으로 선택하고 암·복호화와 MAC 생성·검증을 실행한다.
결합 송신은 MAC-I 생성·추가 후 전체를 암호화한다.
결합 수신은 복호화 후 마지막 유효 32-bit를 분리해 검증한다.
Hex/Bit 길이를 자동 계산하며 선행 0과 비정렬 bit를 보존한다.

### 검증

- Linux 및 실제 Windows EXE 각각 공식 36/36 PASS.
- 자체 통합·경계 unittest test method 21개 PASS.
- 실제 Windows GUI widget 30/30 PASS.
- Windows 11 Home x64에서 EXE 한 개만 복사하고 다른 CWD·개발 런타임 격리 상태로 실행.
- Windows EXE SHA-256: `b27b536b216e8f43c6c390d27262ec6f091a4a51b9c5a6340c8148e3802f4522`.

### 파일

`3GPP-Security-Tools-0.1.0-windows-x64.zip`을 풀고 EXE를 실행한다.
Python이나 별도 라이브러리 설치가 필요 없다.
ZIP은 실행 파일·사용법·검증 보고서·런타임 license notice를 포함한다.
직접 EXE, 소스 ZIP과 SHA256SUMS도 제공한다.

### 남은 항목과 범위

새로 설치한 Windows PC/VM, Windows 10 및 ARM64는 검증하지 않았다.
따라서 전체 배포 완료를 선언하는 최종 릴리스가 아닌 사전 릴리스 후보로 게시한다.
256-bit NEA/NIA는 후속이며 AEAD/NCA는 제외한다.
NAS/PDCP PDU 파싱·보호 영역 자동 구성은 포함하지 않는다.
표준 원문 PDF와 참조 C 코드 전체는 포함하지 않는다.

고정 표준·SAGE 실제 버전·URL·해시·Cip1 매핑은 SOURCES.md, 상세 결과는 VALIDATION.md를 참조한다.
