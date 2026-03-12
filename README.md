# FastAPI Backend

이 프로젝트는 FastAPI 기반 백엔드 서비스입니다.

목표

- 유지보수 가능한 구조
- 명확한 계층 분리
- 테스트 가능한 코드
- 확장 가능한 아키텍처

---

# 기술 스택

- Python 3.11+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Redis
- Pytest
- Docker

---

# 프로젝트 구조
```BASH
backend
├── app
│   ├── main.py
│   ├── api
│   │   └── v1
│   │       └── routers
│   ├── services
│   ├── repositories
│   ├── models
│   ├── schemas
│   ├── core
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── db
│   │   ├── session.py
│   │   └── base.py
│   ├── dependencies
│   └── utils
├── tests
└── alembic
```
---

# 아키텍처

Router → Service → Repository → Database

설명

Router  
- HTTP 요청 처리  
- 입력 검증  
- Service 호출  

Service  
- 비즈니스 로직  

Repository  
- 데이터베이스 접근  

---

# 실행 방법

## 1. 가상 환경 생성

```bash
python -m venv .venv
```

## 2. 가상 환경 활성화

```bash
source .venv/bin/activate
```

Windows PowerShell 에서 실행하는 경우:

```powershell
.venv\Scripts\Activate.ps1
```

## 3. 라이브러리 설치

```bash
pip install -r requirements.txt
```

## 4. 환경 변수 파일 생성

```bash
cp .env.example .env
```

필요한 값은 `.env` 에 맞게 수정합니다.

## 5. 서버 실행

```bash
uvicorn app.main:app --reload
```

## 6. 문서 확인

http://localhost:8000/docs

## Docker Compose로 PostgreSQL / Redis 실행

```bash
docker compose up -d
```

기본 compose 기준 연결 정보

- PostgreSQL: `postgresql+psycopg://user:password@localhost:5432/app`
- Redis: `redis://localhost:6379/0`

---

# 테스트 실행

```bash
pytest
```

---

# 환경 변수

예시는 [.env.example](.env.example) 파일을 참고합니다.

주요 인증 관련 변수

- `SECRET_KEY`: JWT 서명 키
- `ACCESS_TOKEN_EXPIRE_MINUTES`: access token 만료 시간(분)
- `REFRESH_TOKEN_EXPIRE_DAYS`: refresh token 만료 시간(일)
- `REDIS_URL`: refresh token 상태 저장용 Redis 주소
- `SEED_USER_EMAIL`: 기본 로그인 계정 이메일
- `SEED_USER_PASSWORD`: 기본 로그인 계정 비밀번호
- `APP_LOG_DIR`: 애플리케이션 로그 저장 디렉터리
- `APP_LOG_LEVEL`: 애플리케이션 로그 레벨
- `APP_LOG_BACKUP_COUNT`: 일 단위 로그 파일 보관 개수

PostgreSQL 사용 시 `DATABASE_URL`은 `postgresql+psycopg://...` 형식을 사용합니다.

로그는 기본적으로 `app/logs/app.log` 파일에 기록되며, 자정마다 일 단위로 로테이션됩니다.

---

# 인증 API

## 로그인

`POST /api/v1/auth/login`

```json
{
  "email": "admin@example.com",
  "password": "change_me_1234"
}
```

응답 예시

```json
{
  "access_token": "....",
  "refresh_token": "....",
  "token_type": "bearer",
  "access_token_expires_in": 1800,
  "refresh_token_expires_in": 604800
}
```

## Access Token 재발급

`POST /api/v1/auth/refresh`

```json
{
  "refresh_token": "...."
}
```

응답 예시

```json
{
  "access_token": "....",
  "token_type": "bearer",
  "access_token_expires_in": 1800
}
```
