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

backend/
│
├─ app/
│  ├─ main.py
│  ├─ api/
│  │  └─ v1/
│  │     └─ routers/
│  ├─ services/
│  ├─ repositories/
│  ├─ models/
│  ├─ schemas/
│  ├─ core/
│  │  ├─ config.py
│  │  ├─ security.py
│  │  └─ exceptions.py
│  ├─ db/
│  │  ├─ session.py
│  │  └─ base.py
│  ├─ dependencies/
│  └─ utils/
│
├─ tests/
└─ alembic/

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

## 1. 설치

pip install -r requirements.txt

## 2. 서버 실행

uvicorn app.main:app --reload

## 3. 문서 확인

http://localhost:8000/docs

---

# 테스트 실행

pytest

---

# 환경 변수

예시 (.env)

DATABASE_URL=postgresql://user:password@localhost/db
SECRET_KEY=your_secret_key
REDIS_URL=redis://localhost:6379