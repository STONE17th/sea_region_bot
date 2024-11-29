from aiogram import Router

from .command import command_router
from .inline import inline_router

handlers_routers = Router()

handlers_routers.include_routers(
    command_router,
    inline_router,
)

__all__ = [
    'handlers_routers',
]
