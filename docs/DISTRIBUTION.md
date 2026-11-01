# 출처·배포 조건 기록

문서 profile: TECHNICAL_NOTE. 확인일: 2026-11-01.

## 확보한 근거

[ETSI 알고리즘 안내](https://www.etsi.org/expertise/algorithms-codes/)는 UEA2/UIA2와 EEA3/EIA3에 Restricted Usage Undertaking 안내를 제공한다.
[GSMA 공식 안내](https://www.gsma.com/solutions-and-impact/technologies/security/security-algorithms/)도 구현·사용 조건과 ZUC 관련 별도 권리 안내를 제공한다.
원문 다운로드와 알고리즘 사용 조건의 법적 적용 범위는 구분한다.

이 프로젝트는 normative 알고리즘에 따라 Python 코드를 작성했다.
외부 C 구현이나 C 확장 라이브러리를 제품에 포함하지 않는다.
SNOW SQ와 ZUC S-box/D 상수는 확보한 SAGE 원문의 알고리즘 상수이다.
공식 테스트 값은 원문에서 전사했다.
원문 PDF와 참조 C 코드 전체는 공개 대상에 포함하지 않는다.

## 현재 상태

공개 대상은 독립 작성 Python 코드, 전사한 테스트 입력·기대값, 계산 결과·보고서 및 연구용 GUI 배포 후보이다.
표준 PDF 원문과 참조 C 코드 전체는 공개 대상에서 제외한다.
공식 안내가 이 공개 대상에 각각 어떻게 적용되는지에 대한 법적 판단은 수행하지 않았다.
알고리즘 특허·사용 약정의 적용 여부와 권리 확보 여부를 테스트 결과로 증명할 수는 없다.
이 프로젝트는 알고리즘 권리의 법적 확인 완료를 주장하지 않는다.

## 포함 런타임과 개발 의존성

배포 EXE는 CPython 3.12.10, Tcl/Tk 8.6과 PyInstaller bootloader/runtime hook을 포함한다.
배포 ZIP에는 해당 배포판의 license notice를 함께 넣는다.
PyInstaller·hook·setuptools·pefile 등 빌드 의존성의 정확한 버전은 `packaging/requirements-windows.txt`에 기록한다.
PyInstaller의 실행 파일 배포 예외는 [공식 license 설명](https://pyinstaller.org/en/stable/license.html)을 참조한다.
이 설명이 3GPP 알고리즘의 사용 권한을 대신하지 않는다.
