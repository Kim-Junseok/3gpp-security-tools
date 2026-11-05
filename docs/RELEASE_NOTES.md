# 릴리스 기록

## v0.1.0-rc5 — 수신 입력 통일

- `Received MAC-I` 입력 칸을 제거했다.
- Integrity만 사용하는 수신도 원본 데이터와 MAC-I를 한 칸에 입력한다.
- Ciphering을 사용하면 먼저 복호화한 뒤 같은 방식으로 MAC-I를 분리한다.
- 결과에는 분리한 MAC-I와 재계산한 MAC-I를 표시한다.

수신에서는 송신과 같은 MAC 길이를 선택한다. 송신의 독립 MAC 생성 기능은 유지한다.
공식 벡터 135/135, 통합·경계 34개, Windows EXE GUI 201/201 PASS를 확인했다.
새 EXE의 로컬 Windows 11 개발 런타임 격리 실행도 통과했다.
세부 기록은 [VALIDATION.md](VALIDATION.md)에 보관한다.

## v0.1.0-rc4 — 안내 문구 줄바꿈 수정

변환 안내·오류 문구가 창의 실제 가로 폭을 사용하도록 수정했다.
넓은 창에서 불필요한 개행을 줄이고 좁은 창에서는 문장을 읽을 수 있게 줄바꿈한다.
계산 코어와 공식 데이터는 유지했다.
Linux·Windows EXE 공식 벡터 135/135, 통합 31개, Windows EXE GUI 199/199 PASS를 확인했다.
배포 EXE는 Windows CI 빌드를 사용하며 로컬 Windows 11의 개발 런타임 격리 실행도 통과했다.
상세 결과와 초기 로컬 빌드의 실행 차단 기록은 [VALIDATION.md](VALIDATION.md)에 남겼다.

## v0.1.0-rc3 — 영문 GUI·256-bit NEA/NIA

- GUI 전체를 영어로 전환하고 작은 화면에서 입력·결과를 스크롤할 수 있게 했다.
- 256-bit NEA4/NIA4·NEA5/NIA5·NEA6/NIA6을 추가했다.
- 48-bit EXTRA_IV와 NIA4~6의 4~16-byte MAC-I를 지원한다.
- 기존 legacy 0~3과 Hex/Bit 입력·공통 탭 설정·결합 송신·수신을 유지한다.

공식 벡터는 legacy 36 + 추가 NEA/NIA 72 + primitive 27 = 135건이다.
이번 Linux와 Windows 11 EXE에서 각각 135/135 PASS, 통합 테스트 31개 PASS, Windows EXE GUI 197/197 PASS를 확인했다.
Windows CI에서 검증한 EXE를 그대로 사용하고 로컬에서 개발 런타임을 격리해 다시 실행했다.
EXE SHA-256: `fc45b468faa1489cabc9fc74768d77e3e8ff64d73bb74b04452314cebd2129e7`.

Windows ZIP을 풀고 EXE를 실행한다. Python이나 별도 라이브러리를 설치할 필요가 없다.
GitHub 릴리스 제목·본문과 `RUNNING.txt`는 영어, 저장소와 배포물의 `.md` 문서는 한글로 제공한다.
rc1·rc2의 태그·첨부 파일은 보존하고 GitHub 제목·본문만 영어로 바꾼다.
새 Windows PC/VM, 서로 다른 DPI 모니터 이동, Windows 10·ARM64는 검증하지 않았다.
상세 결과는 [VALIDATION.md](VALIDATION.md)를 따른다.

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
