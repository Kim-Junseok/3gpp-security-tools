# 후속 작업

## 남은 검증

- 새 Windows PC/VM에서 Python·개발 도구를 설치한 적 없는 상태로 실행한다.
- 서로 다른 DPI 배율의 모니터 사이에서 창을 이동하며 선명도와 배치를 확인한다.
- Windows 10·ARM64는 아직 실행 검증 범위에 포함하지 않는다.

## 반영 완료

- GUI 영문 전환과 작은 화면용 스크롤.
- 256-bit NEA4/NIA4·NEA5/NIA5·NEA6/NIA6.
- 48-bit EXTRA_IV와 4~16-byte MAC-I 선택.
- TS 35.240~35.248 v20.0.0 원문 기반 공식 벡터와 primitive 검사.

검증한 환경과 실제 결과는 [VALIDATION.md](VALIDATION.md)를 따른다.
AEAD/NCA와 NAS/PDCP PDU 파싱·보호 영역 자동 구성은 구현 범위에서 제외한다.
