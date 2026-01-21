# Backlog: Redis Caching

## [Redis 캐싱 서비스]

### Completed Tests
- [x] Test name: test_cache_set_and_get
- [x] Expected behavior: 캐시에 값 저장 및 조회
- [x] Acceptance criteria: set/get 정상 동작

- [x] Test name: test_cache_get_returns_none_when_not_found
- [x] Expected behavior: 존재하지 않는 키는 None 반환
- [x] Acceptance criteria: None 반환

- [x] Test name: test_cache_delete
- [x] Expected behavior: 캐시에서 키 삭제
- [x] Acceptance criteria: delete 정상 동작

- [x] Test name: test_cache_game_session
- [x] Expected behavior: 게임 세션 캐싱 (TTL 1시간)
- [x] Acceptance criteria: session:{session_id} 키로 저장

- [x] Test name: test_get_cached_session
- [x] Expected behavior: 캐시된 세션 조회
- [x] Acceptance criteria: 세션 데이터 정상 반환

- [x] Test name: test_cache_expression_image
- [x] Expected behavior: 표정 이미지 캐싱 (TTL 24시간)
- [x] Acceptance criteria: expression:{setting_id}:{type} 키로 저장

- [x] Test name: test_get_cached_expression
- [x] Expected behavior: 캐시된 표정 이미지 조회
- [x] Acceptance criteria: 이미지 URL 정상 반환

- [x] Test name: test_cache_special_image
- [x] Expected behavior: 특별 이벤트 이미지 캐싱 (TTL 24시간)
- [x] Acceptance criteria: special:{prompt_hash} 키로 저장

- [x] Test name: test_get_cached_special_image
- [x] Expected behavior: 캐시된 특별 이미지 조회
- [x] Acceptance criteria: 이미지 URL 정상 반환

### Implementation Notes
- CacheService 클래스로 Redis 작업 추상화
- Mock을 사용한 단위 테스트 (실제 Redis 연결 불필요)
- JSON 직렬화/역직렬화 자동 처리

### Cache Keys & TTL
| Key Pattern | TTL | 용도 |
|-------------|-----|------|
| session:{session_id} | 1시간 (3600s) | 게임 세션 상태 |
| expression:{setting_id}:{type} | 24시간 (86400s) | 표정 이미지 URL |
| special:{prompt_hash} | 24시간 (86400s) | 특별 이벤트 이미지 URL |

### Files Changed
- app/services/cache_service.py (new)
- tests/test_redis_cache.py (new)

### Usage Example
```python
from app.services.cache_service import CacheService
import redis.asyncio as redis

# Initialize
redis_client = redis.from_url("redis://localhost:6379")
cache = CacheService(redis_client)

# Session caching
await cache.cache_session(session_id, session_data)
session = await cache.get_session(session_id)

# Expression caching
await cache.cache_expression(setting_id, "happy", image_url)
url = await cache.get_expression(setting_id, "happy")

# Special image caching
await cache.cache_special_image(prompt_hash, image_url)
url = await cache.get_special_image(prompt_hash)
```
