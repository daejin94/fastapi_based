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
