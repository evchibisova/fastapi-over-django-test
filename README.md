# fastapi-over-django-test

Illustration of an article on combining FastAPI and Django.

1. Start the app:
```bash
docker compose up -d --build
```

2. Run the benchmark — three parallel POSTs against an async endpoint (using `sync_to_async` over the Django ORM) and the same against a plain sync route, with per-request timing:
```bash
docker compose exec app bash scripts/bench.sh
```

3. Run tests
```bash
docker compose exec app pytest
```
One test is intentionally marked `xfail`: it creates an`Order` inside pytest-django's uncommitted transaction, while the handler runs on FastAPI's threadpool on a separate Django connection that can't see uncommitted writes, so the lookup returns 404.

4. Stop and drop the postgres volume:
```bash
docker compose down -v
```
