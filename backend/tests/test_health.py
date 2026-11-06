def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_openapi_has_all_tags(client):
    spec = client.get("/openapi.json").json()
    tags = {t["name"] for t in spec["tags"]} if "tags" in spec["info"] else set()
    paths = list(spec["paths"])
    # каркас должен отдавать все ключевые группы эндпоинтов
    for prefix in ["/api/v1/auth", "/api/v1/users", "/api/v1/items",
                   "/api/v1/catalog", "/api/v1/bookings", "/api/v1/wallet",
                   "/api/v1/notifications", "/api/v1/reports", "/api/v1/admin"]:
        assert any(p.startswith(prefix) for p in paths), prefix
