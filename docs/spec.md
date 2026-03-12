# Spec

## 현재 범위

- 인증 API 제공
- 로그인 시 access token, refresh token 발급
- refresh token으로 access token 재발급
- access token 기반 현재 사용자 인증 dependency 제공
- 성공 응답은 공통 `APIResponse` 포맷 사용
- 전역 예외 핸들러를 통한 공통 오류 응답 반환
- 환경 변수 기반 CORS 설정 제공
- 애플리케이션 로그를 파일로 저장
- 로그 파일은 `app/logs` 아래에 일 단위로 로테이션

## 인증 API 요구사항

- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/refresh`
- 요청과 응답은 Pydantic 스키마를 사용

## 인증 Dependency 요구사항

- `Authorization: Bearer <access_token>` 형식의 헤더를 사용한다.
- 인증 dependency는 access token을 검증하고 현재 사용자를 조회해야 한다.
- refresh token은 보호된 엔드포인트 인증에 사용할 수 없어야 한다.
- 별도 요청이 없는 신규 API는 기본적으로 인증 dependency를 적용해야 한다.
- 인증 없이 열어야 하는 공개 API는 요구사항 문서에서 명시적으로 선언해야 한다.

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

## CORS 요구사항

- CORS 허용 Origin, Method, Header는 환경 변수로 관리한다.
- 허용된 Origin은 preflight 요청에 대해 CORS 헤더를 반환해야 한다.
- 허용되지 않은 Origin은 preflight 요청 단계에서 차단해야 한다.
