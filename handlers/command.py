from aiogram import Bot, Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

import os

from database import DataBase
from keyboards import ikb_confirm_admin, ikb_registration
from misc.validators import validate_email, validate_phone
from middleware.middleware import IsRegistered

command_router = Router()
command_router.message.middleware(IsRegistered())


@command_router.message(Command('start'))
async def command_start(message: Message, admin: bool, driver: bool, bot: Bot):
    if admin:
        message_text = 'Вы админ!'
        keyboard = None
    elif driver:
        message_text = 'Вы водитель!'
        keyboard = None
    else:
        message_text = 'Зарегистрируйтесь!'
        keyboard = ikb_registration()
    await message.answer(
        text=message_text,
        reply_markup=keyboard,
    )


@command_router.message(Command('admin', prefix='!'))
async def admin_request(message: Message, command: CommandObject, bot: Bot):
    if command.args and len(command.args.split()) == 2:
        email, phone = command.args.split()
        email, phone = validate_email(email), validate_phone(phone)
        if email and phone:
            if message.from_user.id in DataBase().load_admins():
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text='Вы уже админ!',
                )
            else:
                message_text = f'Пользователь {message.from_user.full_name} ({message.from_user.id})\nСделать админом?'
                await bot.send_message(
                    chat_id=int(os.getenv('SUPER_ADMIN')),
                    text=message_text,
                    reply_markup=ikb_confirm_admin(message.from_user.id, email, phone),
                )
        else:
            message_text = 'Укажите корректный '
            list_errors = []
            if not email:
                list_errors.append('E-Mail (не более 34 символов)')
            if not phone:
                list_errors.append('номер телефона')
            await bot.send_message(
                chat_id=message.from_user.id,
                text=message_text + ' и '.join(list_errors),
            )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text='Введите команду в формате\n!admin <ваш e-mail> <телефон>'
        )
