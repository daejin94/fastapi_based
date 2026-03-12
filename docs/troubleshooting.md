# Troubleshooting

## 2026-03-12 FastAPI 테스트 hang

- 증상: `pytest`에서 `TestClient(app)` 진입 후 인증 API 테스트가 멈춤
- 원인: 현재 실행 환경에서 FastAPI `sync def` 엔드포인트와 동기 의존성의 threadpool 경로가 요청 처리 중 대기 상태에 들어감
- 대응:
  - 인증 라우터와 기본 헬스체크를 `async def`로 변경
  - `get_db`, `get_redis` 의존성을 비동기 형태로 변경
  - 테스트를 `TestClient` 대신 `httpx.AsyncClient`와 `ASGITransport` 기반으로 전환
  - 테스트에서 앱 lifespan은 `app.router.lifespan_context(app)`로 직접 관리
- 결과: 가상환경에서 인증 API 테스트를 정상 실행할 수 있는 구조로 정리
