from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    waiting_product = State()
    waiting_quantity = State()
    waiting_name = State()
    waiting_phone = State()
    confirm = State()