from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from bot.states.order import OrderStates
from bot.keyboards.order import product_keyboard, phone_keyboard, confirm_keyboard, PRODUCTS
from bot.services.api_client import create_order, OrderAPIError
from bot.config import config

router = Router()

PRODUCT_LABELS = dict(PRODUCTS)


@router.message(Command("order"))
async def cmd_order(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Qaysi mahsulotni buyurtma qilmoqchisiz?", reply_markup=product_keyboard())
    await state.set_state(OrderStates.waiting_product)


@router.callback_query(OrderStates.waiting_product, F.data.startswith("product:"))
async def process_product(callback: CallbackQuery, state: FSMContext):
    if not callback.data or not isinstance(callback.message, Message):
        await callback.answer()
        return

    product_value = callback.data.split(":", 1)[1]

    await state.update_data(product_name=product_value)
    await callback.message.edit_text(f"Tanlandi: {PRODUCT_LABELS.get(product_value, product_value)}")
    await callback.message.answer("Nechta dona kerak? (faqat raqam kiriting)")
    await state.set_state(OrderStates.waiting_quantity)
    await callback.answer()


@router.message(OrderStates.waiting_quantity)
async def process_quantity(message: Message, state: FSMContext):
    text = (message.text or "").strip()

    if not text.isdigit() or int(text) <= 0:
        await message.answer("Iltimos, musbat butun son kiriting (masalan: 10).")
        return

    await state.update_data(quantity=int(text))
    await message.answer("Ismingizni kiriting:")
    await state.set_state(OrderStates.waiting_name)


@router.message(OrderStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()

    if not name:
        await message.answer("Iltimos, ismingizni kiriting.")
        return

    await state.update_data(customer_name=name)
    await message.answer(
        "Telefon raqamingizni yuboring:",
        reply_markup=phone_keyboard(),
    )
    await state.set_state(OrderStates.waiting_phone)


@router.message(OrderStates.waiting_phone, F.contact)
async def process_phone_contact(message: Message, state: FSMContext):
    if not message.contact:
        return
    phone = message.contact.phone_number
    await _show_confirmation(message, state, phone)


@router.message(OrderStates.waiting_phone, F.text)
async def process_phone_text(message: Message, state: FSMContext):
    if not message.text:
        return
    phone = message.text.strip()
    await _show_confirmation(message, state, phone)


async def _show_confirmation(message: Message, state: FSMContext, phone: str):
    await state.update_data(customer_phone=phone)
    data = await state.get_data()

    product_label = PRODUCT_LABELS.get(data["product_name"], data["product_name"])

    summary = (
        "Buyurtmangizni tekshiring:\n\n"
        f"📦 Mahsulot: {product_label}\n"
        f"🔢 Miqdor: {data['quantity']}\n"
        f"👤 Ism: {data['customer_name']}\n"
        f"📱 Telefon: {phone}\n\n"
        "To'g'rimi?"
    )

    await message.answer(summary, reply_markup=ReplyKeyboardRemove())
    await message.answer("Tasdiqlaysizmi?", reply_markup=confirm_keyboard())
    await state.set_state(OrderStates.confirm)


@router.callback_query(OrderStates.confirm, F.data == "confirm:no")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    if isinstance(callback.message, Message):
        await callback.message.edit_text("Buyurtma bekor qilindi. Qayta boshlash uchun /order yuboring.")

    await callback.answer()


@router.callback_query(OrderStates.confirm, F.data == "confirm:yes")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    try:
        order = await create_order(
            customer_telegram_id=callback.from_user.id,
            customer_name=data["customer_name"],
            customer_phone=data["customer_phone"],
            product_name=data["product_name"],
            quantity=data["quantity"],
        )
    except OrderAPIError:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                "Kechirasiz, buyurtmani yuborishda xatolik yuz berdi. Birozdan keyin qayta urinib ko'ring."
            )
        await callback.answer()
        return

    await state.clear()

    if isinstance(callback.message, Message):
        await callback.message.edit_text("✅ Buyurtmangiz qabul qilindi! Tez orada siz bilan bog'lanamiz.")

    await callback.answer()

    await _notify_admins(callback, order, data)


async def _notify_admins(callback: CallbackQuery, order: dict, data: dict):
    if callback.bot is None:
        return

    product_label = PRODUCT_LABELS.get(data["product_name"], data["product_name"])
    username = callback.from_user.username or str(callback.from_user.id)

    text = (
        "🆕 Yangi buyurtma!\n\n"
        f"🆔 Order ID: {order['id']}\n"
        f"📦 Mahsulot: {product_label}\n"
        f"🔢 Miqdor: {data['quantity']}\n"
        f"👤 Ism: {data['customer_name']}\n"
        f"📱 Telefon: {data['customer_phone']}\n"
        f"💬 Telegram: @{username}"
    )

    for admin_id in config.admin_chat_ids:
        try:
            await callback.bot.send_message(admin_id, text)
        except Exception:
            continue