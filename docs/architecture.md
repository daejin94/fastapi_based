# Architecture

## 1. 문서 목적

이 문서는 `fastapi_based` 저장소 자체를 설명하는 문서이면서,
동시에 다른 FastAPI 프로젝트를 시작할 때 그대로 가져다 쓸 수 있는
"퀵 스타트 아키텍처 템플릿"을 목적으로 한다.

즉, 이 문서는 완성된 구현 설명서라기보다
새 프로젝트의 기본 구조를 빠르게 잡기 위한 기준 문서다.

---

## 2. 이 템플릿의 사용 방식

새 프로젝트를 시작할 때는 아래 흐름으로 사용한다.

1. 이 저장소 구조를 기본 골격으로 복사한다.
2. 프로젝트 이름, 도메인, 환경 변수, DB 설정을 새 프로젝트에 맞게 바꾼다.
3. 공통 규칙은 유지한 채 기능별 모듈만 추가한다.
4. 첫 기능 구현 전에 이 문서를 기준으로 구조를 다시 점검한다.

이 템플릿이 해결하려는 문제는 다음과 같다.

- 프로젝트 시작할 때 폴더 구조를 매번 새로 고민하는 문제
- Router, Service, Repository 경계가 흐려지는 문제
- 요청/응답 스키마와 ORM 모델이 섞이는 문제
- 초반에는 빠르게 만들었지만 나중에 유지보수가 어려워지는 문제

---

## 3. 템플릿 현재 상태

이 저장소는 의도적으로 최소한의 초기 상태만 가지고 있다.

현재 포함된 것

- FastAPI 앱 진입점 `app/main.py`
- 백엔드 표준 디렉터리 구조
- `core`, `db`, `docs` 기본 파일
- 문서 중심의 작업 관리 구조

아직 비어 있는 것

- 실제 도메인 모델
- 실제 API 라우터
- 서비스 로직
- 리포지토리 구현
- DB 연결 설정
- 인증/인가
- 테스트 코드

이 상태는 미완성이 아니라 "새 프로젝트 시작 직전 상태"에 가깝다.

---

## 4. 기본 디렉터리 구조

```text
app/
  main.py
  api/
    v1/
      routers/
  services/
  repositories/
  models/
  schemas/
  core/
    config.py
    security.py
    exceptions.py
  db/
    session.py
    base.py
  dependencies/
  utils/

tests/
alembic/
docs/
```

각 디렉터리 역할

- `app/main.py`: FastAPI 앱 생성, 전역 설정 시작점
- `app/api/v1/routers`: API 엔드포인트
- `app/services`: 비즈니스 로직
- `app/repositories`: DB 접근 로직
- `app/models`: SQLAlchemy ORM 모델
- `app/schemas`: 요청/응답 Pydantic 스키마
- `app/core`: 설정, 보안, 공통 예외
- `app/db`: DB 세션, Base, 엔진 설정
- `app/dependencies`: FastAPI `Depends()` 공통 의존성
- `app/utils`: 범용 헬퍼
- `tests`: 테스트 코드
- `alembic`: 마이그레이션
- `docs`: 설계, 진행, 결정 기록

---

## 5. 핵심 아키텍처 원칙

이 템플릿은 아래 계층 구조를 기본으로 한다.

```text
Client
  -> Router
  -> Service
  -> Repository
  -> Database
```

### Router

해야 하는 일

- HTTP 요청 받기
- 입력값 검증
- 의존성 주입 연결
- Service 호출
- 응답 반환

하면 안 되는 일

- 비즈니스 로직 작성
- DB 직접 접근
- SQL 실행
- ORM 모델 직접 반환

### Service

해야 하는 일

- 비즈니스 로직 처리
- 도메인 규칙 검증
- Repository 조합
- 도메인 예외 발생

하면 안 되는 일

- HTTP 상태 코드 중심으로 로직 작성
- 라우터 책임까지 가져가기

### Repository

해야 하는 일

- SQLAlchemy 기반 데이터 접근
- 조회/생성/수정/삭제 처리
- 세션 기반 ORM 작업 수행

하면 안 되는 일

- API 응답 형식 판단
- 비즈니스 정책 판단
- FastAPI 의존 로직 작성

---

## 6. 새 프로젝트에서 유지할 것

아래 항목은 새 프로젝트를 만들어도 가능한 한 유지한다.

- `Router -> Service -> Repository -> Database` 흐름
- `/api/v1` prefix
- 요청/응답 스키마 분리
- `response_model` 명시
- DB 접근은 Repository에서만 수행
- 예외는 서비스에서 발생시키고 전역 핸들러에서 HTTP로 변환
- 설정값 하드코딩 금지
- 새 기능에는 테스트 추가

이 항목들은 템플릿의 핵심 규칙이므로 프로젝트마다 바뀌지 않는 기본값으로 본다.

---

## 7. 새 프로젝트에서 바꿔야 할 것

아래 항목은 프로젝트 시작 시점에 맞게 교체하거나 확장한다.

- 프로젝트명
- API 제목과 설명
- 도메인 모델
- DB 종류와 연결 정보
- 인증 방식
- 공통 응답 포맷
- 환경 변수 목록
- 기능별 라우터/서비스/리포지토리

예를 들어 다음은 프로젝트별 커스터마이징 대상이다.

- `app/main.py`의 앱 메타데이터
- `app/core/config.py`의 설정 필드
- `app/core/security.py`의 인증 전략
- `app/models/`, `app/schemas/`, `app/services/`, `app/repositories/` 하위 구현

---

## 8. 권장 구현 순서

새 프로젝트를 이 템플릿으로 시작할 때 권장 순서는 다음과 같다.

1. `requirements.txt` 또는 의존성 관리 파일 정리
2. `app/core/config.py`에 환경 설정 정의
3. `app/db/session.py`에 DB 연결 및 세션 구성
4. `app/api/v1` 라우터 등록 구조 작성
5. 예시 리소스 하나를 골라 전체 흐름 구현
6. `tests/api`, `tests/services`에 테스트 추가
7. Alembic 초기화 및 첫 마이그레이션 준비

처음부터 모든 기능을 만들기보다,
리소스 하나를 기준으로 전체 흐름을 끝까지 관통하는 것이 좋다.

---

## 9. 추천 첫 구현 예시

처음 구현할 리소스는 너무 복잡하지 않은 것이 좋다.

예시

- `users`
- `posts`
- `items`
- `health`

예를 들어 `users`를 선택했다면 다음 구조로 확장할 수 있다.

- `app/api/v1/routers/users.py`
- `app/services/user_service.py`
- `app/repositories/user_repository.py`
- `app/models/user.py`
- `app/schemas/user.py`
- `tests/api/test_users.py`
- `tests/services/test_user_service.py`

이렇게 한 번 패턴을 만들면 이후 기능은 같은 규칙으로 복제하면 된다.

---

## 10. API 설계 기본 규칙

모든 API는 아래 기준을 따른다.

- `/api/v1` prefix 사용
- REST 스타일 유지
- 요청/응답 Schema 분리
- `response_model` 지정
- 별도 요구사항이 없으면 인증이 필요한 보호 API로 설계
- 공개 API는 문서에서 명시적으로 예외 선언

예시

- `GET /api/v1/users/{user_id}`
- `POST /api/v1/users`
- `PATCH /api/v1/users/{user_id}`

스키마 예시

- `UserCreate`
- `UserUpdate`
- `UserRead`

금지

- Router에서 ORM 모델 직접 반환
- 요청 스키마와 응답 스키마를 하나로 합치기

---

## 11. 데이터베이스 원칙

기본 기준 기술은 다음과 같다.

- SQLAlchemy 2.x
- Alembic

원칙

- DB 접근은 Repository에서만 처리
- 명시적 세션 처리 사용
- implicit commit 금지
- 마이그레이션 이력은 Alembic으로 관리

프로젝트에 따라 PostgreSQL, MySQL, SQLite 등으로 바뀔 수 있지만,
계층 분리 원칙은 유지한다.

---

## 12. 예외 처리 원칙

예외는 중앙 집중 방식으로 처리한다.

흐름

- Service에서 도메인 예외 발생
- 전역 exception handler에서 HTTP 응답으로 변환

이 방식을 쓰는 이유

- 서비스 로직이 HTTP 프레임워크 세부사항에 덜 묶인다
- 에러 응답 형식을 일관되게 유지할 수 있다

---

## 13. 테스트 원칙

템플릿 단계부터 테스트 위치를 미리 잡아둔다.

기본 위치

- `tests/api`
- `tests/services`

필요 시 확장

- `tests/repositories`
- `tests/integration`

새 기능을 추가할 때는
"구현 후 테스트 추가"가 아니라
"구조에 맞는 테스트 위치를 함께 만든다"는 기준으로 접근한다.

---

## 14. 문서 구조

이 템플릿은 코드뿐 아니라 문서 스타터 역할도 함께 한다.

- `docs/spec.md`: 요구사항 정리
- `docs/plan.md`: 작업 계획
- `docs/progress.md`: 진행 상태
- `docs/next.md`: 다음 작업
- `docs/decisions.md`: 기술 결정 기록
- `docs/troubleshooting.md`: 문제 해결 기록
- `docs/feature/`: 기능별 상세 문서
- `docs/refactoring/`: 리팩터링 기록
- `docs/architecture.md`: 구조 기준 문서

즉, 새 프로젝트를 시작할 때
코드 구조뿐 아니라 작업 방식까지 같이 복사해 가는 것을 권장한다.

---

## 15. 이 문서를 업데이트하는 시점

아래 경우에는 이 문서를 수정한다.

- 기본 구조가 바뀌었을 때
- 공통 예외 처리 방식이 바뀌었을 때
- 인증 전략이 바뀌었을 때
- 테스트 전략이 바뀌었을 때
- 다른 프로젝트에도 공통으로 반영할 가치가 생겼을 때

반대로 기능 상세 동작은 이 문서보다 `docs/feature/` 쪽에 기록하는 편이 적합하다.

---

## 16. 요약

이 문서는 "현재 구현 설명서"라기보다
"다음 FastAPI 프로젝트를 빨리 시작하기 위한 기준 문서"에 가깝다.

핵심은 다음이다.

- 구조는 미리 단순하게 고정한다
- 책임 분리는 초반부터 강하게 잡는다
- 새 프로젝트마다 바뀌는 부분만 교체한다
- 첫 기능 하나로 전체 패턴을 완성한다
- 문서와 테스트 구조도 함께 시작한다

이 기준을 유지하면 프로젝트를 새로 시작해도
초기 구조 설계에 쓰는 시간을 크게 줄일 수 있다.
