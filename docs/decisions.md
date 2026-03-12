# Decisions

## 2026-03-12 Global Exception 도입

- 서비스 레이어는 FastAPI `HTTPException`을 직접 발생시키지 않는다.
- 서비스는 도메인 의미를 가진 `AppException` 계열 예외를 발생시킨다.
- HTTP 상태 코드와 응답 포맷 변환은 전역 exception handler가 맡는다.
- 인증 실패 응답은 `code`, `detail`을 공통 필드로 사용한다.

## 2026-03-12 성공 응답 래퍼 도입

- 성공 응답은 공통 `APIResponse[T]` 스키마로 감싼다.
- 실제 비즈니스 데이터는 `data` 필드에 위치시킨다.
- 에러 응답은 기존 전역 예외 포맷을 유지하고, 추후 통합 여부를 별도로 결정한다.

## 2026-03-12 파일 로깅 도입

- 애플리케이션 로그는 `app/logs/app.log` 파일에 저장한다.
- 표준 라이브러리 `TimedRotatingFileHandler`로 자정 기준 일 단위 로테이션을 적용한다.
- 요청 완료 로그와 예외 로그는 `app` 로거 계층으로 일원화한다.

## 2026-03-12 API 예시 문서 분리

- README는 프로젝트 소개와 실행 방법 중심으로 유지한다.
- API 요청/응답 예시는 `docs/api-spec.md`에서 별도로 관리한다.

## 2026-03-12 CORS 설정 도입

- CORS 정책은 `app/main.py` 전역 미들웨어로 적용한다.
- 허용 Origin, Method, Header는 환경 변수에서 읽는다.
- 기본값은 빠른 로컬 개발을 위해 와일드카드 허용으로 두고, 환경별로 오버라이드한다.

## 2026-03-12 인증 Dependency 도입

- Bearer access token 검증은 `app/dependencies/auth.py`에서 공통 처리한다.
- 토큰 해석과 사용자 조회는 `AuthService`로 위임해 기존 계층 흐름을 유지한다.
- 보호된 사용자 정보 조회 엔드포인트는 `/api/v1/auth/me`로 제공한다.

## 2026-03-12 신규 API 기본 인증 원칙

- 앞으로 추가하는 API는 별도 요청이 없으면 기본적으로 인증이 필요한 보호 API로 구현한다.
- 인증 예외가 필요한 공개 API는 요구사항과 문서에서 명시적으로 선언한다.
