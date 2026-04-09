# 086: Request Caching with Redis

## Phase
All Phases

## Description
Cache repeated queries for performance.

## Requirements
- Redis integration
- Cache key strategy
- TTL configuration
- Cache invalidation

## Acceptance Criteria
- [ ] Repeated queries cached
- [ ] Cache hit rate visible
- [ ] Automatic expiration
- [ ] Manual purge option

## Related Files
- `src/db.py` - Redis cache integration
- `src/services/cache.py` - Cache service

## Dependencies
- 006: Send Message to LLM
