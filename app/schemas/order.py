from pydantic import BaseModel, ConfigDict
from enum import Enum
from datetime import datetime
from typing import Optional


class OrderStatus(str, Enum):
    new = 'yangi'
    bajar = 'topshirildi'
    cancel = 'bekor qilindi'


class Product(str, Enum):
    tuxum = 'tuxum'


class OrderCreate(BaseModel):
    customer_telegram_id: int
    customer_name: str
    customer_phone: str
    product_name: Product
    quantity: int


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    product_name: Optional[Product] = None
    quantity: Optional[int] = None
    status: Optional[OrderStatus] = None


class OrderResponse(BaseModel):
    id: int
    customer_telegram_id: int
    customer_name: str
    customer_phone: str
    product_name: Product
    quantity: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)