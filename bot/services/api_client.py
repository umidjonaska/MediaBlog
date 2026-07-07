import httpx

from bot.config import config


class OrderAPIError(Exception):
    pass


async def create_order(
    customer_telegram_id: int,
    customer_name: str,
    customer_phone: str,
    product_name: str,
    quantity: int,
) -> dict:
    payload = {
        "customer_telegram_id": customer_telegram_id,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "product_name": product_name,
        "quantity": quantity,
    }

    async with httpx.AsyncClient(base_url=config.api_base_url, timeout=10.0) as client:
        try:
            response = await client.post("/order", json=payload)
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise OrderAPIError(f"Backend xato qaytardi: {e.response.text}") from e
        except httpx.RequestError as e:
            raise OrderAPIError(f"Backendga ulanib bo'lmadi: {e}") from e

        return response.json()