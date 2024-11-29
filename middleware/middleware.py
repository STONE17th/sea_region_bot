from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from database import DataBase


class IsRegistered(BaseMiddleware):

    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any],
                       ) -> Any:
        data['admin'] = event.from_user.id in DataBase().admins
        data['driver'] = event.from_user.id in DataBase().drivers
        return await handler(event, data)
