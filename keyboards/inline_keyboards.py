from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data import ConfirmRegistration, DataValue


def ikb_confirm_admin(user_tg_id: int, email: str, phone: str):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Принять',
        callback_data=ConfirmRegistration(
            request='ra',
            response=True,
            tg_id=user_tg_id,
            email=email,
            phone=phone,
        )
    )
    keyboard.button(
        text='Отмена',
        callback_data=ConfirmRegistration(
            request='ra',
            response=False,
            tg_id=user_tg_id,
            email=email,
            phone=phone,
        )
    )
    return keyboard.as_markup()


def ikb_registration(driver_tg_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Регистрация',
        callback_data=DataValue(
            button='driver_registration',
            value=str(driver_tg_id),
        )
    )
    return keyboard.as_markup()


def ikb_confirm_driver(driver_tg_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Принять',
        callback_data=ConfirmRegistration(
            request='cd',
            response=True,
        )
    )
    keyboard.button(
        text='Назад',
        callback_data=DataValue(
            button='registration_back',
            value=str(driver_tg_id),
        )

    )
    keyboard.button(
        text='Отмена',
        callback_data=DataValue(
            button='cancel',
            value=str(None),
        )
    )
    return keyboard.as_markup()


def ikb_back_registration(driver_tg_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Назад',
        callback_data=DataValue(
            button='registration_back',
            value=str(driver_tg_id),
        )
    )
    return keyboard.as_markup()


def ikb_cancel():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Отмена',
        callback_data=DataValue(
            button='cancel',
            value=str(None),
        )
    )
    return keyboard.as_markup()
