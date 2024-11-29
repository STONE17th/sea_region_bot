from aiogram import Router

from .drivers_fsm import driver_router

fsm_routers = Router()
fsm_routers.include_routers(
    driver_router,
)

__all__ = [
    'fsm_routers',
]
