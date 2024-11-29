import os
import asyncio

from aiogram import Bot, Dispatcher

from database import DataBase
from handlers import handlers_routers
from fsm import fsm_routers

bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()

dp.include_routers(
    handlers_routers,
    fsm_routers,
)


def on_start():
    print('Bot is started...')
    print('Connect to DataBase:', end=' ')
    try:
        DataBase().create_tables()
    except Exception as e:
        print(f'Failure...\n{e}')
    else:
        print('OK!')


def on_shutdown():
    print('Bot is down now!')


async def start_bot():
    dp.startup.register(on_start)
    dp.shutdown.register(on_shutdown)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(start_bot())
