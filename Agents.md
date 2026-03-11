# Agents.md

이 문서는 AI 코딩 에이전트가 이 저장소에서 코드를 생성할 때 따라야 하는 규칙을 정의합니다.

---

# 기본 원칙

- 코드 일관성을 가장 중요하게 고려한다.
- 기존 코드 스타일을 우선적으로 따른다.
- 불필요한 추상화나 복잡한 설계를 만들지 않는다.

---

# 아키텍처 규칙

프로젝트는 다음 구조를 따른다.

Router → Service → Repository → Database

Router

역할

- HTTP 요청 처리
- 입력 검증
- Service 호출

Router는 다음을 하면 안 된다.

- 비즈니스 로직 작성
- 데이터베이스 직접 접근
- SQL 실행

---

Service

역할

- 비즈니스 로직
- Repository 호출
- 도메인 검증

---

Repository

역할

- 데이터베이스 접근
- ORM 쿼리 처리

Repository는 API 로직을 알면 안 된다.

---

# API 규칙

모든 API는 다음 규칙을 따른다.

- `/api/v1` prefix 사용
- REST 스타일 유지
- response_model 반드시 지정
- 요청/응답은 Pydantic Schema 사용

예시

GET /api/v1/users/{user_id}

POST /api/v1/users

PATCH /api/v1/users/{user_id}

---

# Schema 규칙

요청과 응답 Schema는 반드시 분리한다.

예시

UserCreate
UserUpdate
UserRead

Router에서 ORM 모델을 직접 반환하면 안 된다.

---

# Database 규칙

- SQLAlchemy 2.x 사용
- Alembic으로 마이그레이션 관리
- DB 접근은 Repository에서만 수행

금지

- Router에서 DB 접근
- implicit commit

---

# 의존성 주입

FastAPI Depends()를 사용한다.

예시

- DB Session
- 현재 사용자
- 공통 서비스

---

# 예외 처리

예외는 중앙에서 처리한다.

규칙

- 서비스에서 도메인 예외 발생
- 글로벌 exception handler에서 HTTP 변환

---

# 테스트

새로운 기능은 테스트를 포함해야 한다.

테스트 위치

tests/api/
tests/services/

pytest 사용

---

# 보안

다음 규칙을 반드시 지킨다.

- 평문 비밀번호 저장 금지
- 비밀키 하드코딩 금지
- 입력값 검증 필수
- 민감 정보 로그 기록 금지