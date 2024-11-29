from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_list, Italic

from database import DataBase
from keyboards import ikb_confirm_driver, ikb_back_registration, ikb_cancel
from keyboards.callback_data import Button, ConfirmRegistration
from misc.validators import validate_phone, validate_passport
from .states import DriverRegistration, caption_from_state

driver_router = Router()

DRIVER_CAPTION_FIELDS = {
    'name': 'ФИО',
    'passport': 'Паспорт',
    'phone': 'Телефон',
}

DRIVER_INIT_DATA = {
    'driver_tg_id': None,
    'message_id': None,
    'name': None,
    'passport': None,
    'phone': None,
    'back': False,
}


def update_adapter(update: CallbackQuery | Message) -> tuple[int, int, str | None]:
    if isinstance(update, CallbackQuery):
        return update.from_user.id, update.message.message_id, None
    return update.from_user.id, update.message_id, update.text


async def delete_message(state: FSMContext, chat_id: int, message_id: int, bot: Bot):
    data = await state.get_data()
    if not data['back']:
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
    await state.update_data(back=False)


@driver_router.callback_query(DriverRegistration(), Button.filter(F.button == 'driver_registration_back'))
async def back_step(update: CallbackQuery | Message, state: FSMContext, bot: Bot):
    await state.update_data(back=True)
    current_step = await state.get_state()
    if current_step == DriverRegistration.get_driver_passport:
        await state.update_data(name=None)
        await state.set_state(DriverRegistration.get_driver_name)
        await driver_name_request(update, state, bot)
    elif current_step == DriverRegistration.get_driver_phone:
        await state.update_data(passport=None)
        await state.set_state(DriverRegistration.get_driver_passport)
        await driver_phone_request(update, state, bot)
    elif current_step == DriverRegistration.confirm_driver_data:
        await state.update_data(phone=None)
        await state.set_state(DriverRegistration.get_driver_phone)
        await confirm_driver_request(update, state, bot)


@driver_router.callback_query(Button.filter(F.button == 'driver_registration'))
async def driver_name_request(callback: CallbackQuery, state: FSMContext, bot: Bot):
    chat_id, message_id, message_text = update_adapter(callback)
    current_state = await state.get_state()
    if not current_state:
        await state.update_data(**DRIVER_INIT_DATA)
    await state.update_data(
        message_id=message_id,
        back=False,
    )
    await state.set_state(DriverRegistration.get_driver_name)
    caption = await caption_from_state(state, message='Введите свои ФИО', **DRIVER_CAPTION_FIELDS)
    await bot.edit_message_text(
        **caption,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=ikb_cancel(),
    )


@driver_router.message(DriverRegistration.get_driver_name)
async def driver_passport_request(message: Message, state: FSMContext, bot: Bot):
    chat_id, message_id, message_text = update_adapter(message)
    state_data = await state.get_data()
    await delete_message(
        state=state,
        chat_id=chat_id,
        message_id=message_id,
        bot=bot,
    )
    await state.update_data(name=message_text)
    caption = await caption_from_state(
        state=state,
        message='Введите свои паспортные данные:',
        **DRIVER_CAPTION_FIELDS,
    )
    await bot.edit_message_text(
        **caption,
        chat_id=chat_id,
        message_id=state_data['message_id'],
        reply_markup=ikb_back_registration(),
    )
    await state.set_state(DriverRegistration.get_driver_passport)


@driver_router.message(DriverRegistration.get_driver_passport)
async def driver_phone_request(message: Message, state: FSMContext, bot: Bot):
    chat_id, message_id, message_text = update_adapter(message)
    await delete_message(
        state=state,
        chat_id=chat_id,
        message_id=message_id,
        bot=bot,
    )
    await state.update_data(passport=message_text)
    state_data = await state.get_data()
    # driver_passport = validate_passport(state_data['passport'])
    driver_passport = state_data['passport']
    if driver_passport:
        await state.set_state(DriverRegistration.get_driver_phone)
        await state.update_data(
            passport=driver_passport,
        )
    msg = [
        ['Введите корректные серию и номер паспорта'],
        ['Введите свой контактный номер телефона'],
    ]
    caption = await caption_from_state(
        state=state,
        message=msg[bool(driver_passport)],
        **DRIVER_CAPTION_FIELDS,
    )
    await bot.edit_message_text(
        **caption,
        chat_id=chat_id,
        message_id=state_data['message_id'],
        reply_markup=ikb_back_registration(),
    )


@driver_router.message(DriverRegistration.get_driver_phone)
async def confirm_driver_request(message: Message, state: FSMContext, bot: Bot):
    chat_id, message_id, message_text = update_adapter(message)
    await delete_message(
        state=state,
        chat_id=chat_id,
        message_id=message_id,
        bot=bot,
    )
    state_data = await state.get_data()
    # await state.update_data(phone=message_text)
    # driver_phone = validate_phone(message_text)
    driver_phone = message_text
    msg = ['Введите корректный номер телефона']
    keyboard = ikb_back_registration()
    if driver_phone:
        await state.set_state(DriverRegistration.confirm_driver_data)
        await state.update_data(
            phone=driver_phone,
        )
        msg = [
            'Данные введены верно?',
            Italic(f'Нажимая "Принять" вы даете согласие на обработку персональных данных'),
        ]
        keyboard = ikb_confirm_driver()
    caption = await caption_from_state(
        state=state,
        message=msg,
        **DRIVER_CAPTION_FIELDS,
    )
    await bot.edit_message_text(
        **caption,
        chat_id=message.from_user.id,
        message_id=state_data['message_id'],
        reply_markup=keyboard,
    )


@driver_router.callback_query(DriverRegistration.confirm_driver_data, ConfirmRegistration.filter(F.request == 'cd'))
async def confirm_driver(callback: CallbackQuery, callback_data: ConfirmRegistration, state: FSMContext, bot: Bot):
    await state.update_data(driver_tg_id=callback.from_user.id)
    state_data = await state.get_data()
    state_data.pop('message_id')
    state_data.pop('back')
    print(*state_data.items())
    # if callback_data.response:
    #     DataBase().add_driver(**state_data)
    #     await callback.answer(
    #         text='Ваш профиль успешно добавлен в базу!',
    #         show_alert=True,
    #     )
    # else:
    #     pass
    # await bot.delete_message(
    #     chat_id=callback.from_user.id,
    #     message_id=callback.message.message_id,
    # )
