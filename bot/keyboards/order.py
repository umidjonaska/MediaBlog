from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

# Hozircha faqat bitta mahsulot bor (backend'dagi Product enum bilan sinxron
# saqlang: app/schemas/order.py -> Product). Kelajakda yangi mahsulot qo'shsangiz,
# bu yerga ham qo'shishni unutmang.
PRODUCTS = [
    ("tuxum", "🥚 Tuxum"),
]


def product_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"product:{value}")]
        for value, label in PRODUCTS
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm:yes"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="confirm:no"),
            ]
        ]
    )