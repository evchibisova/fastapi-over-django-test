import pytest
from fastapi.testclient import TestClient

from app.asgi import app
from app.infrastructure.models import Order


@pytest.mark.xfail(
    strict=True,
    reason=(
        "pytest-django wraps the test in an uncommitted transaction; the FastAPI "
        "TestClient runs the sync handler on a separate Django connection that "
        "can't see those uncommitted writes, so the lookup returns 404."
    ),
)
@pytest.mark.django_db
def test_get_order_returns_existing_order():
    """GET /orders/{id} returns the order created in the test body."""
    Order.objects.create(id=1, amount=10)
    response = TestClient(app).get("/orders/1")
    assert response.status_code == 200


@pytest.mark.django_db(transaction=True)
def test_get_order_returns_existing_order_with_transaction_true():
    """Same test, but the fixture commits writes (transaction=True)."""
    Order.objects.create(id=1, amount=10)
    response = TestClient(app).get("/orders/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1
