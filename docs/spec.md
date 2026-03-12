# Spec

## 현재 범위

- 인증 API 제공
- 로그인 시 access token, refresh token 발급
- refresh token으로 access token 재발급
- 성공 응답은 공통 `APIResponse` 포맷 사용
- 전역 예외 핸들러를 통한 공통 오류 응답 반환
- 애플리케이션 로그를 파일로 저장
- 로그 파일은 `app/logs` 아래에 일 단위로 로테이션

## 인증 API 요구사항

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- 요청과 응답은 Pydantic 스키마를 사용

## 예외 응답 요구사항

- 서비스 레이어는 `HTTPException` 대신 도메인 예외를 발생시킨다.
- FastAPI 전역 exception handler가 도메인 예외를 HTTP 응답으로 변환한다.
- 공통 오류 응답은 `code`, `detail` 필드를 포함한다.
- 요청 검증 실패는 `validation_error` 코드와 검증 오류 목록을 반환한다.

## 성공 응답 요구사항

- 성공 응답은 `success`, `data`, `message` 필드를 포함한다.
- 실제 응답 데이터는 `data` 내부에 위치한다.
- 기본 성공 응답의 `success` 값은 `true`이다.
- 성공 응답의 `message`는 별도 안내가 없으면 `null`이다.

## 로깅 요구사항

- 앱 로그는 `app/logs/app.log`에 기록한다.
- 로그 디렉터리가 없으면 앱 시작 시 자동 생성한다.
- 로그 파일은 일 단위로 분리되도록 설정한다.
- 요청 처리 결과와 예외 처리 결과를 추적할 수 있어야 한다.
