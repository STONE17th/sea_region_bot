from aiogram.utils.keyboard import InlineKeyboardBuilder

from .callback_data import ConfirmRegistration, Button


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


def ikb_registration():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Регистрация',
        callback_data=Button(
            button='driver_registration',
        )
    )
    return keyboard.as_markup()


def ikb_confirm_driver():
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
        callback_data=Button(
            button='driver_registration_back',
        )

    )
    keyboard.button(
        text='Отмена',
        callback_data=Button(
            button='cancel',
        )
    )
    return keyboard.as_markup()


def ikb_back_registration():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Назад',
        callback_data=Button(
            button='driver_registration_back',
        )
    )
    keyboard.button(
        text='Отмена',
        callback_data=Button(
            button='cancel',
        )
    )
    return keyboard.as_markup()


def ikb_cancel():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text='Отмена',
        callback_data=Button(
            button='cancel',
        )
    )
    return keyboard.as_markup()
