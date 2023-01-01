from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import loguru
import sys
import funcs
import requests
from blockcypher import get_block_overview
import asyncio

API_TOKEN = input()

# Конфигурация логирования
loguru.logger.add(sink=sys.stderr, format="{time} {level} {message}", level="DEBUG")

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dispatcher = Dispatcher(bot)


@dispatcher.message_handler(commands='start')
async def start_handler(message: types.Message):
    """Хэндлер команды /start"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    loguru.logger.debug(f"Введена команда /start пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAEHEwFjrv_qyP2xoFchsY9jGJEgHqSthAACDgADDkfHKNYTYJGwbH6ZLQQ')
    await bot.send_message(chat_id=chat_id, text=f'Добро пожаловать, {full_name}', parse_mode='HTML')


@dispatcher.message_handler(commands='last')
async def last_block_handler(message: types.Message):
    """Хэндлер команды /last"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    loguru.logger.debug(f"Введена команда /last пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAEHFsljsZ3YlHcbHEvkfh3zY0AWAUyS3gACFQADDkfHKN9bk18wSjcfLQQ')
    text = f'{funcs.last_block()}'
    await bot.send_message(chat_id=chat_id, text=text)
    await bot.send_document(chat_id=chat_id, document='transactions.html')


@dispatcher.message_handler(commands='exchange')
async def last_block_handler(message: types.Message):
    """Хэндлер команды /exchange"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    loguru.logger.debug(f"Введена команда /exchange пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    await bot.send_sticker(chat_id=chat_id,
                           sticker='CAACAgIAAxkBAAEHFs1jsaDbck0XvCpkZtB9Xr-E5GIeNAACNAADDkfHKERK3MnaPtY3LQQ')
    text = f'{funcs.cryptocurrency_exchange_rate()}'
    await bot.send_message(chat_id=chat_id, text=text)


@dispatcher.message_handler()
async def process_name_step(message: types.Message):
    chat_id = message.chat.id
    msg_id = message.message_id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    if '/block' in message.text:
        loguru.logger.debug(f"Введена команда /block пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        block_id = message.text.split(' ')
        await bot.send_sticker(chat_id=chat_id,
                               sticker='CAACAgIAAxkBAAEHFsljsZ3YlHcbHEvkfh3zY0AWAUyS3gACFQADDkfHKN9bk18wSjcfLQQ')
        text = f'{funcs.block_by_number(block_id)}'
        await bot.send_message(chat_id=chat_id, text=text)
        await bot.send_document(chat_id=chat_id, document='transactions.html')
    if '/balance' in message.text:
        loguru.logger.debug(f"Введена команда /balance пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
        await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        addr = message.text.split(' ')
        await bot.send_sticker(chat_id=chat_id,
                               sticker='CAACAgIAAxkBAAEHFstjsaCTSoIUS14J7IibcWJxvPN0egACOAADDkfHKLFQmvkn6ZxTLQQ')
        text = f'{funcs.btc_adress_balance(addr)}'
        await bot.send_message(chat_id=chat_id, text=text)


if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dispatcher)
