"""Applicationlarni yig'ish"""
import uvicorn

from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette import status
from starlette.responses import JSONResponse

from core.config import config
from utils.slack import send_slack_message

from api import app

# Corsga ruxsat berish
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP javoblarini siqish uchun ishlatiladi, bu resurslarni uzatishni tezlashtiradi va tarmoqli resurslarni tejaydi.
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=4)

# Fayl va rasimlarni yuklash uchun papka
#app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Xatolik haqida ma'lumotlar olish
    exc_type = type(exc).__name__
    exc_message = str(exc)

    # Slacga yuborish
    send_slack_message(exc, exc_type, exc_message)

    # Foydalanuvchiga javob
    if not config.debug:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Serverda kutilmagan xatolik yuz berdi."}
        )

if __name__ == "__main__":
    uvicorn.run("main:app",host="127.0.0.1", port=8000,
                log_level="info", reload=False)