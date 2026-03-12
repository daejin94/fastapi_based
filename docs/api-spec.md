# API Spec

## 문서 목적

- 이 문서는 현재 제공 중인 API 호출 예시를 별도로 관리하기 위한 문서다.
- README에는 진입 안내만 남기고, 실제 요청/응답 예시는 이 문서에 모은다.

## 공통 사항

- API prefix는 `/api/v1`을 사용한다.
- 인증 관련 성공 응답은 공통 `APIResponse` 래퍼 내부 `data`에 위치한다.
- 실행 중인 Swagger 문서는 `http://localhost:8000/docs`에서 확인할 수 있다.

## 인증 API

### 로그인

`POST /api/v1/auth/login`

요청 예시

```json
{
  "email": "admin@example.com",
  "password": "change_me_1234"
}
```

응답 예시

```json
{
  "success": true,
  "data": {
    "access_token": "....",
    "refresh_token": "....",
    "token_type": "bearer",
    "access_token_expires_in": 1800,
    "refresh_token_expires_in": 604800
  },
  "message": null
}
```

### Access Token 재발급

`POST /api/v1/auth/refresh`

요청 예시

```json
{
  "refresh_token": "...."
}
```

응답 예시

```json
{
  "success": true,
  "data": {
    "access_token": "....",
    "token_type": "bearer",
    "access_token_expires_in": 1800
  },
  "message": null
}
```
