from aiogram.fsm.state import State, StatesGroup


class DriverRegistration(StatesGroup):
    driver_name = State()
    driver_passport = State()
    driver_phone = State()
    driver_confirm = State()
