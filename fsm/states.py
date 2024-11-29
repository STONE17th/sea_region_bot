from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.formatting import as_list


class DriverRegistration(StatesGroup):
    get_driver_name = State()
    get_driver_passport = State()
    get_driver_phone = State()
    confirm_driver_data = State()


async def caption_from_state(state: FSMContext, message: list[str] | str = None, value: str = 'Н/А', **kwargs) -> dict:
    message_rows = []
    data = await state.get_data()
    for field, name in kwargs.items():
        message_rows.append(f'{name}: {data[field] or value}')
    if message:
        if isinstance(message, list):
            message_rows += [' ', *message]
        else:
            message_rows += [' ', message]
    return as_list(*message_rows).as_kwargs()
