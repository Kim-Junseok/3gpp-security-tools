# 후속 구현 목록

문서 profile: TECHNICAL_NOTE. 256-bit 계열은 현재 실행 프로그램에서 미지원이다.
아래 자료 미확보 상태는 legacy 공식 36건의 분모와 분리한다.

| 계열 | 명세 | implementation data | design conformance data | 상태 |
|---|---|---|---|---|
| SNOW 5G NEA4/NIA4 | TS 35.240 | TS 35.241 | TS 35.242 | 후속 / 정확한 버전·NEA/NIA 목록·원문·벡터 미확보 |
| AES NEA5/NIA5 | TS 35.243 | TS 35.244 | TS 35.245 | 후속 / 정확한 버전·NEA/NIA 목록·원문·벡터 미확보 |
| ZUC NEA6/NIA6 | TS 35.246 | TS 35.247 | TS 35.248 | 후속 / 정확한 버전·NEA/NIA 목록·원문·벡터 미확보 |

후속 착수 시 9개 문서를 각각 확보하고 실제 버전·절·URL·SHA-256을 기록한다.
Document 2와 3의 NEA/NIA 필수 케이스를 모두 등록한다.
NCA 전용 항목은 제외한다.
입력 파라미터와 MAC 길이는 각 명세에서 확인한다.
legacy의 32-bit MAC-I 규칙을 그대로 적용하지 않는다.

LLM adapter와 NAS/PDCP PDU 파싱은 현재 구현에 포함하지 않는다.
AEAD/NCA는 현재 및 요청된 후속 구현 범위에서 제외한다.
