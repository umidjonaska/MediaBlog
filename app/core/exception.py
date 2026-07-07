from fastapi import HTTPException, status
from pydantic import BaseModel
from starlette.responses import JSONResponse


class MessageResponse(BaseModel):
    detail: str


class CreatedResponse(JSONResponse):
    def __init__(self, detail: str = "Ma'lumot muvaffaqiyatli yaratildi.", status_code: int = 201):
        content = {"detail": detail}
        super().__init__(content=content, status_code=status_code)


class UpdatedResponse(JSONResponse):
    def __init__(self, detail: str = "Ma'lumot muvaffaqiyatli yangilandi.", status_code: int = 200):
        content = {"detail": detail}
        super().__init__(content=content, status_code=status_code)


class DeletedResponse(JSONResponse):
    def __init__(self, detail: str = "Ma'lumot muvaffaqiyatli o‘chirildi.", status_code: int = 200):
        content = {"detail": detail}
        super().__init__(content=content, status_code=status_code)


class NotFoundResponse(JSONResponse):
    def __init__(self, detail: str = "So‘ralgan ma'lumot topilmadi.", status_code: int = 404):
        content = {"detail": detail}
        super().__init__(content=content, status_code=status_code)


class FailedSchemaResponse(BaseModel):
    key: str | None = None
    detail: str


class FailedResponse(JSONResponse):
    def __init__(self, key: str, detail: str = "Ma'lumot yaratishda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.",
                 status_code: int = 400):
        content = {"key": key, "detail": detail}
        super().__init__(content=content, status_code=status_code)