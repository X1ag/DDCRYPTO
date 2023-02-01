from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import Document, Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Filter
import loguru
import sys
from funcs import *
import requests
from blockcypher import get_block_overview
import asyncio
import os
import pickle
from loguru import logger

try:
    # Читаем переменную data из файла 'save.pkl'
    with open('save.pkl', 'rb') as read:
        API_TOKEN = pickle.load(read)
except:
    API_TOKEN = input('Введите API токен:\n> ')
    # Сохраняем переменную data в файл 'save.pkl'
    with open('save.pkl', 'wb') as write:
        pickle.dump(API_TOKEN, write)

# Конфигурация логирования
loguru.logger.add(
    "logs/{time:YYYY-MM-DD}.log",
    rotation="7 days",
    level="DEBUG"
)


class CallbackDataFilter(Filter):
    def __init__(self, data: str):
        self.data = data

    async def check(self, callback_query: CallbackQuery):
        return callback_query.data == self.data


# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)
loguru.logger.debug('Бот был запущен')


class Form(StatesGroup):
    block_id = State()
    addr = State()


inline_keyboard = InlineKeyboardMarkup()

button_last = InlineKeyboardButton('🔍 Последний блок', callback_data='last')
button_exchange = InlineKeyboardButton('💰 Курс Биткоина', callback_data='exchange')
button_block = InlineKeyboardButton('🔗 Информация о блоке', callback_data='block')
button_balance = InlineKeyboardButton('💼 Биткоин кошелек', callback_data='balance')
inline_keyboard.add(button_last)
inline_keyboard.add(button_exchange)
inline_keyboard.add(button_block)
inline_keyboard.add(button_balance)

menu_keyboard = InlineKeyboardMarkup()

menu_button_text = InlineKeyboardButton('◀️ В меню', callback_data='menu')

menu_keyboard.add(menu_button_text)

menu_sticker = 'CAACAgIAAxkBAAEHi25j2o75xyB-m8C3s4ITgCo7JWPEmQACph8AAv0RsEpbI3U8YSp1vy4E'
last_sticker = 'CAACAgIAAxkBAAEHi4Nj2pISiR7ub3J2ZJoFKgpZLkCFagACKCkAAtjzqErya_sR6K2N4i4E'
exchange_sticker = 'CAACAgIAAxkBAAEHi4Vj2pI1uvDP9bz6NoJuw0kX9rz7tQAC7i4AAu6RsEpU_iAgu_9-aS4E'
block_sticker = 'CAACAgIAAxkBAAEHi4lj2pJS89tE80V_ZHZuAc2G046hYAACGSsAAgREqErosNZKKuXTDC4E'
balance_sticker = 'CAACAgIAAxkBAAEHi5Zj2pUrlw0OKm70CCTKPpUB9KqN9gACVyUAAsoEqUp6NgKY6HXb-S4E'
error_sticker = 'CAACAgIAAxkBAAEHi5Fj2pUO7WE5dh8RaOOAzL-5LslsIAACkCwAAvLrqUr7GbPrm5Xk9C4E'

menu = '''
🔥 <b>Меню:</b>

💰 <b>Курс Биткоина:</b> Получите актуальный курс Биткоина на Blockchain
🔍 <b>Последний блок:</b> Получите информацию о последнем блоке в сети Биткоин, включая транзакции
💼 <b>Биткоин кошелек:</b> Получите информацию о вашем Биткоин кошельке, включая баланс, общую сумму поступлений и выводов
🔗 <b>Информация о блоке:</b> Получите информацию о конкретном блоке по его номеру
'''


@logger.catch
@dispatcher.message_handler(commands='start')
async def start_handler(message: types.Message):
    """Хэндлер команды /start"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    loguru.logger.info(f"Введена команда /start пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    await bot.send_sticker(chat_id=chat_id,
                           sticker=menu_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await bot.send_message(chat_id=chat_id, text=menu, parse_mode='HTML', reply_markup=inline_keyboard)


@logger.catch
@dispatcher.message_handler(commands='last')
async def last_block_handler(message: types.Message):
    """Хэндлер команды /last"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    loguru.logger.info(f"Введена команда /last пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    await bot.send_sticker(chat_id=chat_id,
                           sticker=last_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    text = f'{await last_block()}'
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
    await bot.send_chat_action(chat_id, types.ChatActions.UPLOAD_DOCUMENT)
    await asyncio.sleep(1)
    await bot.send_document(chat_id=chat_id, document=open('transactions.html', 'rb'), reply_markup=menu_keyboard)


@logger.catch
@dispatcher.message_handler(commands='exchange')
async def exchange_handler(message: types.Message):
    """Хэндлер команды /exchange"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    loguru.logger.info(
        f"Введена команда /exchange пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    await bot.send_sticker(chat_id=chat_id,
                           sticker=exchange_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    text = f'{await cryptocurrency_exchange_rate()}'
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML', reply_markup=menu_keyboard)


@logger.catch
@dispatcher.message_handler(commands='block')
async def block_handler(message: types.Message, state: FSMContext):
    """Хэндлер команды /block"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    msg_id = message.message_id
    loguru.logger.info(f"Введена команда /block пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    global msgg_id, stick_id, stickwel_id
    try:
        _, block_id = message.text.split()
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        stickwel_id = (await bot.send_sticker(chat_id=chat_id,
                                              sticker=block_sticker)).message_id
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        text = f'{await block_by_number(block_id)}'
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
        if text != '❌ Введен неверный ID блока!':
            await bot.send_chat_action(chat_id, types.ChatActions.UPLOAD_DOCUMENT)
            await asyncio.sleep(1)
            await bot.send_document(chat_id=chat_id, document=open('transactions.html', 'rb'), reply_markup=menu_keyboard)
        else:
            await bot.delete_message(chat_id=chat_id, message_id=stickwel_id)
    except:
        stick_id = (await bot.send_sticker(chat_id=chat_id,
                                           sticker=block_sticker)).message_id
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await Form.block_id.set()
        msgg_id = (await message.reply("Введите идентификатор блока:")).message_id


@dispatcher.message_handler(state=Form.block_id)
async def process_block_id(message: types.Message, state: FSMContext):
    """
    Process block_id
    """
    chat_id = message.chat.id
    msg_id = message.message_id

    async with state.proxy() as data:
        data['block_id'] = message.text
        await state.finish()

    block_id = data['block_id']
    try:
        block_id = int(block_id)
    except ValueError:
        await bot.send_sticker(chat_id=chat_id,
                               sticker=error_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await bot.delete_message(chat_id=chat_id, message_id=stick_id)
    await bot.delete_message(chat_id=chat_id, message_id=msgg_id)
    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    stickwel_id = (await bot.send_sticker(chat_id=chat_id,
                                          sticker=block_sticker)).message_id
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    text = f'{await block_by_number(block_id)}'
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
    if text != '❌ Введен неверный ID блока!':
        await bot.send_chat_action(chat_id, types.ChatActions.UPLOAD_DOCUMENT)
        await asyncio.sleep(1)
        await bot.send_document(chat_id=chat_id, document=open('transactions.html', 'rb'), reply_markup=menu_keyboard)
    else:
        await bot.delete_message(chat_id=chat_id, message_id=stickwel_id)


@logger.catch
@dispatcher.message_handler(commands='balance')
async def balance_handler(message: types.Message):
    """Хэндлер команды /balance"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    msg_id = message.message_id
    global command
    command = msg_id
    loguru.logger.info(
        f"Введена команда /balance пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    try:
        _, addr = message.text.split()
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        text = f'{await btc_adress_balance(addr)}'
        if text != '❌ Введен неверный адрес кошелька!':
            await bot.send_sticker(chat_id=chat_id,
                                   sticker=balance_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML', reply_markup=menu_keyboard)
    except:
        global msgg_id, stick_id
        stick_id = (await bot.send_sticker(chat_id=chat_id,
                                           sticker=balance_sticker)).message_id
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await Form.addr.set()
        msgg_id = (await message.reply("Введите адрес кошелька:")).message_id


@dispatcher.message_handler(state=Form.addr)
async def process_addr(message: types.Message, state: FSMContext):
    """
    Process address
    """
    chat_id = message.chat.id
    msg_id = message.message_id
    async with state.proxy() as data:
        data['addr'] = message.text
        await state.finish()
    addr = data['addr']
    await bot.delete_message(chat_id=chat_id, message_id=command)
    await bot.delete_message(chat_id=chat_id, message_id=stick_id)
    await bot.delete_message(chat_id=chat_id, message_id=msgg_id)
    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    text = f'{await btc_adress_balance(addr)}'
    if text != '❌ Введен неверный адрес кошелька!':
        await bot.send_sticker(chat_id=chat_id,
                               sticker=balance_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML', reply_markup=menu_keyboard)


# Добавляем возможность отмены, если пользователь передумал заполнять
@logger.catch
@dispatcher.message_handler(state='*', commands='cancel')
@dispatcher.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Отменено')


@dispatcher.callback_query_handler(CallbackDataFilter(data='last'))
async def process_callback_last(callback_query: CallbackQuery):
    """Хэндлер команды /last"""
    chat_id = callback_query.message.chat.id
    user_id = callback_query.message.from_user.id
    full_name = callback_query.message.from_user.full_name
    username = callback_query.message.from_user.username
    await bot.send_sticker(chat_id=chat_id,
                           sticker=last_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    text = f'{await last_block()}'
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
    await bot.send_chat_action(chat_id, types.ChatActions.UPLOAD_DOCUMENT)
    await asyncio.sleep(1)
    await bot.send_document(chat_id=chat_id, document=open('transactions.html', 'rb'), reply_markup=menu_keyboard)


@dispatcher.callback_query_handler(CallbackDataFilter(data='exchange'))
async def process_callback_exchange(callback_query: CallbackQuery):
    """Хэндлер команды /exchange"""
    chat_id = callback_query.message.chat.id
    user_id = callback_query.message.from_user.id
    full_name = callback_query.message.from_user.full_name
    username = callback_query.message.from_user.username
    await bot.send_sticker(chat_id=chat_id,
                           sticker=exchange_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    text = f'{await cryptocurrency_exchange_rate()}'
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML', reply_markup=menu_keyboard)


@dispatcher.callback_query_handler(CallbackDataFilter(data='block'))
async def process_callback_block(callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.message.from_user.id
    full_name = callback_query.message.from_user.full_name
    username = callback_query.message.from_user.username
    msg_id = callback_query.message.message_id
    global msgg_id, stick_id, stickwel_id
    stick_id = (await bot.send_sticker(chat_id=chat_id,
                                       sticker=block_sticker)).message_id
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await Form.block_id.set()
    message = await bot.send_message(callback_query.from_user.id, "Введите идентификатор блока:")
    msgg_id = message.message_id


@dispatcher.callback_query_handler(CallbackDataFilter(data='balance'))
async def process_callback_block(callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.message.from_user.id
    full_name = callback_query.message.from_user.full_name
    username = callback_query.message.from_user.username
    msg_id = callback_query.message.message_id
    global command
    command = msg_id
    global msgg_id, stick_id
    stick_id = (await bot.send_sticker(chat_id=chat_id,
                                       sticker=balance_sticker)).message_id
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await Form.addr.set()
    message = await bot.send_message(callback_query.from_user.id, "Введите адрес кошелька:")
    msgg_id = message.message_id


@dispatcher.callback_query_handler(CallbackDataFilter(data='menu'))
async def process_callback_block(callback_query: CallbackQuery):
    chat_id = callback_query.message.chat.id
    user_id = callback_query.message.from_user.id
    full_name = callback_query.message.from_user.full_name
    username = callback_query.message.from_user.username
    loguru.logger.info(f"Вызвано меню пользователем")
    await bot.send_sticker(chat_id=chat_id, sticker=menu_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await bot.send_message(chat_id=chat_id, text=menu, parse_mode='HTML', reply_markup=inline_keyboard)


if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dispatcher)
