import pytest
import pytest_asyncio

from sqlalchemy import select
from typing import Any

from app.models.order import Order
from app.repositories.order import OrderRepository
from app.schemas.order import OrderCreate, OrderUpdate, Product, OrderStatus


@pytest_asyncio.fixture
async def order_repo(session):
    return OrderRepository(session)


def make_order_payload(**overrides: Any) -> OrderCreate:
    data: dict[str, Any] = dict(
        customer_telegram_id=123456789,
        customer_name="Aziz",
        customer_phone="+998901234567",
        product_name=Product.tuxum,
        quantity=10,
    )
    data.update(overrides)
    return OrderCreate(**data)


@pytest.mark.asyncio
async def test_create_order(order_repo, session):
    payload = make_order_payload()

    created = await order_repo.create_order(payload)

    assert created.id is not None
    assert created.customer_name == "Aziz"
    assert created.quantity == 10
    assert created.status == OrderStatus.new

    result = await session.execute(select(Order).where(Order.id == created.id))
    db_order = result.scalar_one()

    assert db_order.customer_telegram_id == 123456789
    assert db_order.product_name == Product.tuxum


@pytest.mark.asyncio
async def test_get_one_order(order_repo):
    created = await order_repo.create_order(make_order_payload(customer_name="Vali"))

    fetched = await order_repo.get_one_order(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.customer_name == "Vali"


@pytest.mark.asyncio
async def test_get_one_order_not_found(order_repo):
    fetched = await order_repo.get_one_order(9999)

    assert fetched is None


@pytest.mark.asyncio
async def test_get_all_order(order_repo):
    await order_repo.create_order(make_order_payload(customer_name="User1"))
    await order_repo.create_order(make_order_payload(customer_name="User2"))

    orders = await order_repo.get_all_order()

    assert len(orders) == 2
    names = {o.customer_name for o in orders}
    assert names == {"User1", "User2"}


@pytest.mark.asyncio
async def test_get_all_order_excludes_deleted(order_repo):
    o1 = await order_repo.create_order(make_order_payload(customer_name="Active"))
    o2 = await order_repo.create_order(make_order_payload(customer_name="ToDelete"))

    await order_repo.delete_order(o2.id)

    orders = await order_repo.get_all_order()
    names = {o.customer_name for o in orders}

    assert "Active" in names
    assert "ToDelete" not in names


@pytest.mark.asyncio
async def test_update_order(order_repo):
    created = await order_repo.create_order(make_order_payload(quantity=5))

    updated = await order_repo.update_order(
        created.id,
        OrderUpdate(quantity=20, status=OrderStatus.bajar),
    )

    assert updated.quantity == 20
    assert updated.status == OrderStatus.bajar
    assert updated.customer_name == "Aziz"  # o'zgarmagan


@pytest.mark.asyncio
async def test_update_order_not_found(order_repo):
    with pytest.raises(Exception):  # HTTPException 404
        await order_repo.update_order(9999, OrderUpdate(quantity=1))


@pytest.mark.asyncio
async def test_delete_order(order_repo, session):
    created = await order_repo.create_order(make_order_payload())

    deleted = await order_repo.delete_order(created.id)

    assert deleted is True

    result = await session.execute(select(Order).where(Order.id == created.id))
    db_order = result.scalar_one()

    assert db_order.is_deleted is True
    assert db_order.deleted_at is not None

    fetched = await order_repo.get_one_order(created.id)
    assert fetched is None


@pytest.mark.asyncio
async def test_delete_order_not_found(order_repo):
    result = await order_repo.delete_order(9999)

    assert result is None


@pytest.mark.asyncio
async def test_delete_order_already_deleted(order_repo):
    created = await order_repo.create_order(make_order_payload())

    await order_repo.delete_order(created.id)
    second_attempt = await order_repo.delete_order(created.id)

    assert second_attempt is None