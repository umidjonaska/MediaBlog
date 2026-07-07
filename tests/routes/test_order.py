import pytest
import pytest_asyncio

from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserRole
from app.schemas.order import Product, OrderStatus


@pytest_asyncio.fixture
async def user_repo(session):
    return UserRepository(session)


@pytest_asyncio.fixture
async def admin_user(user_repo):
    payload = UserCreate(
        username="adminuser",
        email="admin@mail.ru",
        role=UserRole.ADMIN,
        password_hash="123",
    )
    return await user_repo.create_user(payload)


@pytest_asyncio.fixture
async def regular_user(user_repo):
    payload = UserCreate(
        username="regularuser",
        email="regular@mail.ru",
        role=UserRole.USER,
        password_hash="123",
    )
    return await user_repo.create_user(payload)


@pytest_asyncio.fixture
async def admin_client(client, admin_user):
    """
    get_current_user va get_current_admin_user ikkalasini ham override qiladi.
    """
    from app.auth.services import get_current_user
    from app.api import app

    async def override_get_current_user():
        return {"id": admin_user.id, "email": admin_user.email, "role": admin_user.role.value}

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client


@pytest_asyncio.fixture
async def regular_client(client, regular_user):
    from app.auth.services import get_current_user
    from app.api import app

    async def override_get_current_user():
        return {"id": regular_user.id, "email": regular_user.email, "role": regular_user.role.value}

    app.dependency_overrides[get_current_user] = override_get_current_user
    yield client


def order_payload(**overrides):
    data = dict(
        customer_telegram_id=123456789,
        customer_name="Aziz",
        customer_phone="+998901234567",
        product_name="tuxum",
        quantity=10,
    )
    data.update(overrides)
    return data


@pytest.mark.asyncio
async def test_create_order_no_auth_required(client):
    response = await client.post("/order", json=order_payload())

    assert response.status_code == 201
    data = response.json()
    assert data["customer_name"] == "Aziz"
    assert data["status"] == OrderStatus.new.value


@pytest.mark.asyncio
async def test_get_all_orders_requires_admin(regular_client):
    response = await regular_client.get("/order")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_all_orders_requires_auth(client):
    response = await client.get("/order")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_orders_with_admin(admin_client):
    await admin_client.post("/order", json=order_payload(customer_name="First"))

    response = await admin_client.get("/order")

    assert response.status_code == 200
    data = response.json()
    names = {item["customer_name"] for item in data["data"]}
    assert "First" in names


@pytest.mark.asyncio
async def test_get_one_order_with_admin(admin_client):
    create_response = await admin_client.post("/order", json=order_payload(customer_name="Solo"))
    order_id = create_response.json()["id"]

    response = await admin_client.get(f"/order/{order_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["customer_name"] == "Solo"


@pytest.mark.asyncio
async def test_get_one_order_not_found(admin_client):
    response = await admin_client.get("/order/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_one_order_forbidden_for_regular_user(regular_client, admin_client):
    create_response = await admin_client.post("/order", json=order_payload())
    order_id = create_response.json()["id"]

    response = await regular_client.get(f"/order/{order_id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_order_with_admin(admin_client):
    create_response = await admin_client.post("/order", json=order_payload(quantity=5))
    order_id = create_response.json()["id"]

    response = await admin_client.put(
        f"/order/{order_id}",
        json={"quantity": 25, "status": "topshirildi"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 25
    assert data["status"] == "topshirildi"


@pytest.mark.asyncio
async def test_update_order_forbidden_for_regular_user(regular_client, admin_client):
    create_response = await admin_client.post("/order", json=order_payload())
    order_id = create_response.json()["id"]

    response = await regular_client.put(f"/order/{order_id}", json={"quantity": 1})

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_order_not_found(admin_client):
    response = await admin_client.put("/order/9999", json={"quantity": 1})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_order_with_admin(admin_client, session):
    from sqlalchemy import select
    from app.models.order import Order

    create_response = await admin_client.post("/order", json=order_payload())
    order_id = create_response.json()["id"]

    response = await admin_client.delete(f"/order/{order_id}")

    assert response.status_code == 200

    result = await session.execute(select(Order).where(Order.id == order_id))
    db_order = result.scalar_one()

    assert db_order.is_deleted is True


@pytest.mark.asyncio
async def test_delete_order_forbidden_for_regular_user(regular_client, admin_client):
    create_response = await admin_client.post("/order", json=order_payload())
    order_id = create_response.json()["id"]

    response = await regular_client.delete(f"/order/{order_id}")

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_order_not_found(admin_client):
    response = await admin_client.delete("/order/9999")

    assert response.status_code == 404