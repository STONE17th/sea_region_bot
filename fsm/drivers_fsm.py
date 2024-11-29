from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_list, Italic

from database import DataBase
from keyboards import ikb_confirm_driver, ikb_back_registration, ikb_cancel
from keyboards.callback_data import DataValue, ConfirmRegistration
from misc.validators import validate_phone, validate_passport
from .states import DriverRegistration

driver_router = Router()


def update_adapter(update: CallbackQuery | Message) -> tuple[int, int, str | None]:
    if isinstance(update, CallbackQuery):
        return update.from_user.id, update.message.message_id, None
    return update.from_user.id, update.message_id, update.text


async def message_text_to_dict(state: FSMContext, input_msg: list[str] | None = None):
    state_data = await state.get_data()
    name = state_data['name']
    passport = state_data['passport']
    phone = state_data['phone']
    msg_text = [
        f'{'ФИО':<8}: {name}',
        f'{'Паспорт':<8}: {passport}',
        f'{'Телефон':<8}: {phone}',
    ]
    if input_msg:
        msg_text.append(' ')
        msg_text += input_msg
    return as_list(*msg_text).as_kwargs()


async def delete_message(state: FSMContext, chat_id: int, message_id: int, bot: Bot):
    data = await state.get_data()
    if data['status'] != 'back':
        await bot.delete_message(
            chat_id=chat_id,
            message_id=message_id,
        )
    await state.update_data(status='input')


@driver_router.callback_query(DriverRegistration(), DataValue.filter(F.button == 'registration_back'))
async def back_step(update: CallbackQuery | Message, callback_data: DataValue, state: FSMContext, bot: Bot):
    await state.update_data(status='back')
    current_step = await state.get_state()
    if current_step == DriverRegistration.driver_phone:
        await state.update_data(passport='Н/А')
        await get_driver_name(update, state, bot)
    elif current_step == DriverRegistration.driver_passport:
        await state.update_data(name='Н/А')
        await driver_registration_init(update, callback_data, state, bot)
    elif current_step == DriverRegistration.driver_confirm:
        await state.update_data(phone='Н/А')
        await get_driver_passport(update, state, bot)


@driver_router.callback_query(DataValue.filter(F.button == 'driver_registration'))
async def driver_registration_init(callback: CallbackQuery, callback_data: DataValue, state: FSMContext, bot: Bot):
    chat_id, message_id, message_text = update_adapter(callback)
    current_state = await state.get_state()
    if not current_state:
        await state.update_data(
            driver_tg_id=int(callback_data.value),
            main_fsm_message=message_id,
            name='NA',
            passport='NA',
            phone='NA',
        )
    await state.update_data(status='input')
    await state.set_state(DriverRegistration.driver_name)
    caption = await message_text_to_dict(
        state=state,
        input_msg=['Введите свои ФИО:'],
    )
    await bot.edit_message_text(
        **caption,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=ikb_cancel(),
    )


@driver_router.message(DriverRegistration.driver_name)
async def get_driver_name(message: Message, state: FSMContext, bot: Bot):
    chat_id, message_id, message_text = update_adapter(message)
    state_data = await state.get_data()
    await delete_message(
        state=state,
        chat_id=chat_id,
        message_id=message_id,
        bot=bot,
    )
    await state.set_state(DriverRegistration.driver_passport)
    if message_text:
        await state.update_data(
            name=message_text.title(),
        )
    caption = await message_text_to_dict(
        state=state,
        input_msg=['Введите свои паспортные данные:'],
    )
    await bot.edit_message_text(
        **caption,
        chat_id=chat_id,
        message_id=state_data['main_fsm_message'],
        reply_markup=ikb_back_registration(state_data['driver_tg_id']),
    )


@driver_router.message(DriverRegistration.driver_passport)
async def get_driver_passport(message: Message, state: FSMContext, bot: Bot):
    chat_id, message_id, message_text = update_adapter(message)
    await delete_message(
        state=state,
        chat_id=chat_id,
        message_id=message_id,
        bot=bot,
    )
    if message_text:
        await state.update_data(passport=message_text)
    state_data = await state.get_data()
    passport = state_data['passport']
    driver_passport = validate_passport(passport)
    if driver_passport:
        await state.set_state(DriverRegistration.driver_phone)
        await state.update_data(
            passport=driver_passport,
        )
    msg = [
        ['Введите корректные серию и номер паспорта'],
        ['Введите свой контактный номер телефона'],
    ]
    caption = await message_text_to_dict(
        state=state,
        input_msg=msg[bool(driver_passport)],
    )
    await bot.edit_message_text(
        **caption,
        chat_id=chat_id,
        message_id=state_data['main_fsm_message'],
        reply_markup=ikb_back_registration(state_data['driver_tg_id']),
    )


@driver_router.message(DriverRegistration.driver_phone)
async def get_driver_phone(message: Message, state: FSMContext, bot: Bot):
    chat_id, message_id, message_text = update_adapter(message)
    await delete_message(
        state=state,
        chat_id=chat_id,
        message_id=message_id,
        bot=bot,
    )
    state_data = await state.get_data()
    if message_text:
        await state.update_data(phone=message_text)

    driver_phone = validate_phone(message_text)
    msg = ['Введите корректный номер телефона']
    keyboard = ikb_back_registration(state_data['driver_tg_id'])
    if driver_phone:
        await state.set_state(DriverRegistration.driver_confirm)
        await state.update_data(
            phone=driver_phone,
        )
        msg = [
            'Данные введены верно?',
            Italic(f'Нажимая "Принять" вы даете согласие на обработку персональных данных'),
        ]
        keyboard = ikb_confirm_driver(state_data['driver_tg_id'])
    caption = await message_text_to_dict(
        state=state,
        input_msg=msg,
    )
    await bot.edit_message_text(
        **caption,
        chat_id=message.from_user.id,
        message_id=state_data['main_fsm_message'],
        reply_markup=keyboard,
    )


@driver_router.callback_query(DriverRegistration.driver_confirm, ConfirmRegistration.filter(F.request == 'cd'))
async def driver_confirm(callback: CallbackQuery, callback_data: ConfirmRegistration, state: FSMContext, bot: Bot):
    state_data = dict(await state.get_data())
    state_data.pop('main_fsm_message')
    if callback_data.response:
        DataBase().add_driver(**state_data)
        await callback.answer(
            text='Ваш профиль успешно добавлен в базу!',
            show_alert=True,
        )
    else:
        pass
    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )
