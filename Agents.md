# Agents.md

이 문서는 AI 코딩 에이전트가 이 저장소에서 코드를 생성하거나 수정할 때 따라야 하는 규칙을 정의한다.

---

## 1. 작업 절차

이 프로젝트의 작업 절차는 `Workflow.md`를 따른다.

코드를 작성하거나 수정하기 전에 반드시 다음 문서를 확인한다.

1. `Workflow.md` → 작업 절차
2. `docs/architecture.md` → 시스템 아키텍처 및 계층 구조
3. `docs/spec.md` → 기능 요구사항
4. `docs/plan.md` → 구현 계획
5. `docs/progress.md` → 현재 진행 상태
6. `docs/next.md` → 다음 작업

작업 흐름은 다음 순서를 따른다.

1. `Workflow.md` 확인
2. `docs/` 문서 확인
3. 현재 상태 요약
4. 사용자 승인
5. 코드 작성 또는 수정

---

## 2. 기존 코드 우선 원칙

새로운 코드를 생성하거나 수정할 때 다음 우선순위를 따른다.

1. 기존 프로젝트 코드 패턴
2. `AGENTS.md` 규칙
3. `Workflow.md` 작업 절차
4. 일반 FastAPI 관례

기존 저장소에 이미 정착된 패턴이 있다면 그 방식을 우선 적용한다.

금지 사항

- 기존 구조를 무시한 새 아키텍처 도입
- 동일 목적의 유틸/헬퍼 중복 생성
- 기존 레이어를 우회하는 직접 호출
- 기존 코드 스타일과 다른 네이밍/구조 임의 도입

---

## 3. 프로젝트 아키텍처 규칙

프로젝트는 다음 구조를 따른다.

Router → Service → Repository → Database

### Router

역할

- HTTP 요청 처리
- 입력 검증
- Service 호출
- 응답 반환

금지 사항

- 비즈니스 로직 작성
- 데이터베이스 직접 접근
- SQL 실행
- Repository 직접 호출

### Service

역할

- 비즈니스 로직 처리
- 도메인 검증
- Repository 호출 조합
- 예외 발생 처리

금지 사항

- FastAPI 라우팅 책임 포함
- HTTP 응답 직접 구성
- ORM 모델을 그대로 외부 응답으로 반환

### Repository

역할

- 데이터베이스 접근
- ORM 쿼리 처리
- 영속성 책임 수행

금지 사항

- API 로직 포함
- Service 의존
- FastAPI 객체 의존

---

## 4. 레이어 접근 규칙

레이어 간 접근은 다음 방향만 허용한다.

- Router → Service
- Service → Repository
- Repository → Database

허용하지 않는 접근

- Router → Repository
- Router → Database
- Repository → Service
- Repository → Router

추측입니다: 이 규칙이 없으면 에이전트가 가장 자주 구조를 어지럽힌다.

---

## 5. API 규칙

모든 API는 다음 규칙을 따른다.

- `/api/v1` prefix 사용
- REST 스타일 유지
- `response_model` 반드시 지정
- 요청/응답은 Pydantic Schema 사용
- 경로는 리소스 중심으로 설계

예시

- `GET /api/v1/users/{user_id}`
- `POST /api/v1/users`
- `PATCH /api/v1/users/{user_id}`

피해야 할 경로 예시

- `/getUser`
- `/doLogin`
- `/updateUser`

---

## 6. Schema 규칙

요청과 응답 Schema는 반드시 분리한다.

예시

- `UserCreate`
- `UserUpdate`
- `UserRead`

규칙

- Router에서 ORM 모델을 직접 반환하면 안 된다.
- 응답용 Schema와 입력용 Schema를 분리한다.
- 내부 필드가 외부 응답으로 노출되지 않도록 한다.
- 명확한 타입 선언을 사용한다.

---

## 7. Database 규칙

- SQLAlchemy 2.x 사용
- Alembic으로 마이그레이션 관리
- DB 접근은 Repository에서만 수행
- 트랜잭션 처리는 예측 가능하게 유지

금지 사항

- Router에서 DB 접근
- implicit commit
- ORM 모델과 응답 Schema 역할 혼합
- 마이그레이션 없이 스키마 변경

---

## 8. 의존성 주입 규칙

FastAPI `Depends()`를 사용한다.

주요 대상

- DB Session
- 현재 사용자
- 공통 서비스
- 인증/인가 관련 의존성

규칙

- 기존 프로젝트 의존성 주입 방식을 우선 따른다.
- 동일 역할의 의존성 주입 패턴을 새로 만들지 않는다.

---

## 9. 예외 처리 규칙

예외는 중앙에서 처리한다.

규칙

- 서비스 레이어에서 도메인 예외 발생
- 글로벌 exception handler에서 HTTP 응답으로 변환
- 동일한 예외 처리 코드를 여러 라우터에 반복하지 않는다.

금지 사항

- 예외 삼키기
- 에러 원인 없는 광범위한 except 사용
- 라우터마다 중복 `HTTPException` 남발

---

## 10. 테스트 규칙

새로운 기능 또는 의미 있는 변경은 테스트를 포함해야 한다.

테스트 위치

- `tests/api/`
- `tests/services/`
- `tests/repositories/`

규칙

- `pytest` 사용
- 성공 케이스와 실패 케이스를 모두 고려
- 비즈니스 로직은 서비스 테스트 우선
- 커스텀 쿼리는 repository 테스트 고려

---

## 11. 보안 규칙

다음 규칙을 반드시 지킨다.

- 평문 비밀번호 저장 금지
- 비밀키 하드코딩 금지
- 입력값 검증 필수
- 민감 정보 로그 기록 금지
- 인증/인가 로직은 명시적으로 처리
- 클라이언트 입력을 신뢰하지 않는다.

---

## 12. 네이밍 규칙

Python 규칙을 따른다.

### 변수 및 함수

- `snake_case`

### 클래스

- `PascalCase`

### 상수

- `UPPER_SNAKE_CASE`

### Schema 예시

- `UserCreate`
- `UserUpdate`
- `UserRead`

---

## 13. 파일 생성 규칙

필요한 파일만 생성한다.

원칙

- 기존 파일 확장 가능하면 새 파일 생성 금지
- 동일 목적의 util/helper/base 파일 남발 금지
- 불필요한 placeholder 파일 생성 금지
- 기존 프로젝트 구조 밖에 임의 디렉토리 생성 금지

---

## 14. 문서 동기화 규칙

코드 변경과 관련된 문서는 `Workflow.md`에 따라 함께 갱신한다.

주요 대상 문서

- `docs/spec.md`
- `docs/plan.md`
- `docs/progress.md`
- `docs/next.md`
- `docs/decisions.md`
- `docs/troubleshooting.md`

에러를 해결한 경우 원인과 결과를 `docs/troubleshooting.md`에 기록한다.

---

## 15. 커밋 메시지 규칙

커밋 메시지는 다음 회사 컨벤션을 따른다.

---

### Commit Message Structure

#### <제목>

형식

[타입] 제목

규칙

- 필수 입력
- 50자 제한
- 명령형, 현재 시제 사용
- 무엇을 했는지 또는 왜 변경했는지 요약

예시

[Feat] 사용자 회원가입 기능 구현  
[Fix] 로그인 토큰 검증 오류 수정  
[Docs] API 문서 업데이트

---

#### <본문>

형식

번호 목록으로 작성

규칙

- 선택 사항
- 각 줄 70자 제한
- 명령형, 현재 시제 사용

예시

1. 이메일/비밀번호 입력 기능 추가
2. 회원가입 완료 시 인증 메일 발송
3. 사용자 생성 로직 서비스 레이어로 이동

---

### 허용 타입

- [Feat] : 새로운 기능
- [Fix] : 버그 수정
- [Docs] : 문서 변경
- [Refactor] : 코드 리팩토링
- [Test] : 테스트 코드 추가 또는 수정
- [Chore] : 설정, 빌드, 기타 작업

---

### 커밋 작성 원칙

- 하나의 커밋은 하나의 목적만 가진다.
- 여러 기능 변경을 하나의 커밋에 포함하지 않는다.
- 의미 없는 메시지 사용 금지

잘못된 예시

[Feat] 회원가입 기능, 이메일 인증 기능 구현

올바른 예시

[Feat] 회원가입 기능 구현  
[Feat] 이메일 인증 기능 추가

## 16. 브랜치 규칙

브랜치 이름은 다음 형식을 따른다.

`type/short-name`

예시

- `feature/user-auth`
- `fix/login-token-bug`
- `refactor/auth-service`
- `docs/api-guidelines`
- `test/user-service`

허용되는 type

- `feature`
- `fix`
- `refactor`
- `docs`
- `test`
- `chore`

규칙

- 짧고 의미 있게 작성한다.
- 단어 구분은 하이픈(`-`)을 사용한다.
- 작업 목적이 브랜치 이름만 보고 드러나야 한다.

---

## 17. 최종 원칙

에이전트는 항상 다음을 우선한다.

- 일관성
- 기존 코드 존중
- 단순하고 유지보수 가능한 구조
- 문서와 코드의 동기화
- 승인 기반 작업 절차 준수

확실하지 않음: 프로젝트가 커지면 추가 규칙이 더 필요할 수 있다.  
그 경우에는 `docs/architecture.md`와 `AGENTS.md`를 함께 갱신하는 방식이 가장 안정적이다.