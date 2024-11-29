from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from database import DataBase
from keyboards import ikb_registration
from keyboards.callback_data import ConfirmRegistration, DataValue
from middleware.middleware import IsRegistered

inline_router = Router()
inline_router.callback_query.middleware(IsRegistered())


@inline_router.callback_query(ConfirmRegistration.filter(F.request == 'ra'))
async def request_admin(callback: CallbackQuery, callback_data: ConfirmRegistration, bot: Bot):
    if callback_data.response:
        inline_text = 'Заявка принята'
        message_text = 'Ваша заявка принята!\nТеперь вы админ!'
        DataBase().add_admin(
            admin_tg_id=callback_data.tg_id,
            email=callback_data.email,
            phone=callback_data.phone,
        )
    else:
        inline_text = 'Заявка отклонена'
        message_text = 'Ваша заявка отклонена!'
    await callback.answer(
        text=inline_text,
        show_alert=True,
    )
    await bot.send_message(
        chat_id=callback_data.tg_id,
        text=message_text,
    )
    await bot.delete_message(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
    )


@inline_router.callback_query(DataValue.filter(F.button == 'cancel'))
async def command_start(callback: CallbackQuery, state: FSMContext, admin: bool, driver: bool, bot: Bot):
    await state.clear()
    if admin:
        message_text = 'Вы админ!'
        keyboard = None
    elif driver:
        message_text = 'Вы водитель!'
        keyboard = None
    else:
        message_text = 'Зарегистрируйтесь!'
        keyboard = ikb_registration(callback.from_user.id)
    await bot.edit_message_text(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        text=message_text,
        reply_markup=keyboard,
    )
