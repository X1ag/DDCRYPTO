from aiogram.dispatcher.filters import Filter
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup


# Фильтр Callback вызовов Inline-кнопок
class CallbackDataFilter(Filter):
    def __init__(self, data: str):
        self.data = data

    async def check(self, callback_query: CallbackQuery):
        return callback_query.data == self.data


# состояние для получения текста сообщения для рассылки
class BroadcastMessage(StatesGroup):
    Text = State()


# Создание класса с переменными, которые будут принимать значение сообщения пользователя
class Form(StatesGroup):
    block_id = State()
    addr = State()
    watch_addr = State()
