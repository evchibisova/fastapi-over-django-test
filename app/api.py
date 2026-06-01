import threading

from asgiref.sync import sync_to_async
from django.db import connection
from fastapi import APIRouter, HTTPException

from app.infrastructure.models import Order
from app.schemas import Extra, OrderDTO, OrderWithExtra

router = APIRouter()


@router.post("/orders/{order_id}/dispatch", response_model=OrderWithExtra)
async def dispatch_order(order_id: int) -> OrderWithExtra:
    """Async route + sync_to_async; returns order + extra{thread, connection}.

    Every call goes through asgiref's single shared worker thread
    (thread_sensitive=True by default), so three concurrent requests
    queue up instead of running in parallel.
    """
    try:
        return await sync_to_async(get_order_with_sleep)(order_id)
    except Order.DoesNotExist:
        raise HTTPException(status_code=404)


@router.post("/orders/{order_id}/dispatch-sync", response_model=OrderWithExtra)
def dispatch_order_sync(order_id: int) -> OrderWithExtra:
    """Plain sync route; returns order + extra{thread, connection}.

    FastAPI runs sync routes on its own threadpool, so requests run in parallel
    and each reports its own thread and connection.
    """
    try:
        return get_order_with_sleep(order_id)
    except Order.DoesNotExist:
        raise HTTPException(status_code=404)


@router.get("/orders/{order_id}", response_model=OrderDTO)
def read_order(order_id: int) -> OrderDTO:
    """Sync route - gets order from DB."""
    try:
        order = Order.objects.get(id=order_id)
        return OrderDTO(id=order.id, amount=order.amount)
    except Order.DoesNotExist:
        raise HTTPException(status_code=404)


@router.post("/orders/{order_id}", response_model=OrderDTO)
def create_order(order_id: int) -> OrderDTO:
    """Idempotent create — used by bench.sh to set up Order(id=1)."""
    order, _ = Order.objects.get_or_create(
        id=order_id, defaults={"amount": 100}
    )
    return OrderDTO(id=order.id, amount=order.amount)


def get_order_with_sleep(order_id: int) -> OrderDTO:
    """Synchronous Django ORM call with a 3-second DB-side sleep."""
    order = Order.objects.get(id=order_id)
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_sleep(3);")
    extra = Extra(
        thread=threading.get_ident(),
        connection=connection.connection.info.backend_pid,
    )
    return OrderWithExtra(id=order.id, amount=order.amount, extra=extra)
