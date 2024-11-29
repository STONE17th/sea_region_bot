from aiogram.filters.callback_data import CallbackData


class ConfirmRegistration(CallbackData, prefix=''):
    request: str
    response: bool
    tg_id: int | None = None
    email: str | None = None
    phone: str | None = None


class Button(CallbackData, prefix=''):
    button: str


class DataValue(CallbackData, prefix='DV'):
    button: str
    value: str
