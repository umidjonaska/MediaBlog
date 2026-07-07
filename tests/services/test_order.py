import pytest
from unittest.mock import AsyncMock

from app.services.order import OrderService


@pytest.fixture
def repo():
    return AsyncMock()


@pytest.fixture
def service(repo):
    return OrderService(repo)


@pytest.mark.asyncio
async def test_get_all_order(repo, service):
    repo.get_all_order.return_value = ["order1", "order2"]

    result = await service.get_all_order()

    assert result == ["order1", "order2"]
    repo.get_all_order.assert_called_once()


@pytest.mark.asyncio
async def test_get_one_order(repo, service):
    repo.get_one_order.return_value = {"id": 1}

    result = await service.get_one_order(1)

    assert result == {"id": 1}
    repo.get_one_order.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_create_order(repo, service):
    payload = AsyncMock()
    repo.create_order.return_value = {"id": 1, "customer_name": "Aziz"}

    result = await service.create_order(payload)

    assert result == {"id": 1, "customer_name": "Aziz"}
    repo.create_order.assert_called_once_with(payload)


@pytest.mark.asyncio
async def test_update_order(repo, service):
    payload = {"quantity": 5}
    repo.update_order.return_value = {"id": 1, "quantity": 5}

    result = await service.update_order(1, payload)

    assert result == {"id": 1, "quantity": 5}
    repo.update_order.assert_called_once_with(1, payload)


@pytest.mark.asyncio
async def test_delete_order(repo, service):
    repo.delete_order.return_value = True

    result = await service.delete_order(1)

    assert result is True
    repo.delete_order.assert_called_once_with(1)