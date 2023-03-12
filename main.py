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
import schedule
import time
import sqlite3
from aiogram.utils.exceptions import Throttled
import threading
from typing import List

sys.path.append('src')
from dbs import *
from classes import *
from ux_and_ui import *

# Переменная для функции auto_check_exchange(last_buy)
last_buy = 0

# Конфигурация файла с токеном бота
try:
    # Читаем переменную data из файла 'save.pkl'
    with open('save.pkl', 'rb') as read:
        API_TOKEN = pickle.load(read)
except FileNotFoundError:
    API_TOKEN = input('Введите API токен:\n> ')
    # Сохраняем переменную data в файл 'save.pkl'
    with open('save.pkl', 'wb') as write:
        pickle.dump(API_TOKEN, write)


# Список администраторов
ADMIN_IDS = [1074797971, 744246158] # список id администраторов


# Автоматическая проверка курса криптовалюты и информирование всех юзеров о его изменении, если оно равно, либо
# превышает 2%
def auto_check_exchange(last_buy):
    logger.debug('Автоматическая проверка курса криптовалюты...')
    r = requests.get('https://www.blockchain.com/ru/ticker').json()
    if last_buy != 0:
        logger.debug(f'Старый курс: {last_buy} | Новый курс: {r["RUB"]["buy"]}')
        if last_buy / float(r['RUB']['buy']) >= 1.02:
            parse_from_base()
            # Loop through each row and print the id
            for row in subscribers:
                logger.debug(f'Рассылка: ID{row}')
                requests.get(
                    f'https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={row}&text=❗ Курс упал '
                    f'на {((last_buy / float(r["RUB"]["buy"])) * 100 - 100):.3f}%')

        elif float(r['RUB']['buy']) / last_buy >= 1.02:
            parse_from_base()
            # Loop through each row and print the id
            for row in subscribers:
                logger.debug(f'Рассылка: ID{row}')
                requests.get(f'https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={row}&text=❗ Курс вырос '
                            f'на {((last_buy / float(r["RUB"]["buy"])) * 100 - 100):.3f}%')

    last_buy = r['RUB']['buy']


# Автоматическая проверка баланса криптокошелька
def auto_check_wallet():
    logger.debug('Автоматическая проверка баланса криптокошельков...')
    subscribers = parse_from_base_wallet()
    for row in subscribers:
        wallet = get_wallet(row)
        balance = f'{btc_adress_change(wallet)}'

        if balance != f'{get_old_balance(row)}' and float(balance.split(":")[0]) > float(get_old_balance(row).split(":")[0]):
            btc_diff = float(balance.split(":")[0]) - float(get_old_balance(row).split(":")[0])
            rub_diff = float(balance.split(":")[1]) - float(get_old_balance(row).split(":")[1])
            requests.get(f'https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={row}&text=❗ Кошелек пополнен на {btc_diff:.3f} BTC ({rub_diff:.3f} RUB)')
        elif balance != f'{get_old_balance(row)}' and float(balance.split(":")[0]) < float(get_old_balance(row).split(":")[0]):
            btc_diff = float(get_old_balance(row).split(":")[0]) - float(balance.split(":")[0])
            rub_diff = float(get_old_balance(row).split(":")[1]) - float(balance.split(":")[1])
            requests.get(f'https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={row}&text=❗ С кошелька выведено {btc_diff:.3f} BTC ({rub_diff:.3f} RUB)')

        conn = sqlite3.connect('dbs/subscribers.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE wallet_watcher SET balance = ? WHERE chat_id = ?", (balance, row))
        conn.commit()
        time.sleep(5)



def start_funcs():
    """
    It's a function that runs a function every minute, and that function runs two other functions in
    parallel
    """
    t1 = threading.Thread(target=auto_check_exchange, args=(last_buy,))
    t2 = threading.Thread(target=auto_check_wallet)
    t1.start()
    t2.start()

def kicker():
    """
    It runs the start_funcs function every minute.
    """
    start_funcs()
    schedule.every(15).minutes.do(job_func=start_funcs)
    while True:
        schedule.run_pending()
        time.sleep(900)


# Creating a thread that will run the function kicker()
t = threading.Thread(target=kicker)
t.start()

# Конфигурация логирования
logs_dir = "logs"
log_filename = "log.log"

if not os.path.exists(logs_dir):
    os.mkdir(logs_dir)

logger.add(
    f"{logs_dir}/{log_filename}",
    rotation="1 day",
    level="DEBUG",
    backtrace=True,
    retention="8 days"
)

if not os.path.exists('dbs'):
    os.mkdir('dbs')


# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dispatcher = Dispatcher(bot, storage=storage)


async def anti_flood(*args, **kwargs):
    m = args[0]
    user_id = str(m.from_user.id)
    logger.warning(f"Обнаружен спаммер: ID: {user_id}")
    await m.answer("Не спамьте, иначе вы будете заблокированы")


loguru.logger.debug('Бот был запущен')


@logger.catch
@dispatcher.message_handler(commands='start')
@dispatcher.throttled(anti_flood, rate=3)
async def start_handler(message: types.Message):
    """Хэндлер команды /start"""
    create_users_table()
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    message_id = message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    
    # Проверяем, есть ли пользователь в базе данных
    conn = sqlite3.connect('dbs/users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE chat_id = ?', (chat_id,))
    data = cursor.fetchone()
    
    if data is None:
        # Если пользователь не найден, записываем его в базу данных и выводим уведомление
        cursor.execute('INSERT INTO users VALUES (?)', (chat_id,))
        conn.commit()
        logger.info(f"Новый пользователь: {full_name}, ID: {user_id}, юзернейм: {username}")
    else:
        # Если пользователь уже есть в базе данных, выводим уведомление о введении команды
        logger.info(f"Введена команда /start пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    
    conn.close()
    
    await bot.send_sticker(chat_id=chat_id,
                           sticker=menu_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await bot.send_message(chat_id=chat_id, text=menu, parse_mode='HTML', reply_markup=start_menu)


@logger.catch
@dispatcher.message_handler(commands='last')
@dispatcher.throttled(anti_flood, rate=3)
async def last_block_handler(message: types.Message):
    """Хэндлер команды /last"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    message_id = message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    loguru.logger.info(f"Введена команда /last пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    await bot.send_sticker(chat_id=chat_id,
                           sticker=last_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    wait_id = (await bot.send_message(chat_id, '⚙️ <b>Подготавливаем данные, это может занять некоторое время...</b>',
                                      parse_mode='HTML')).message_id
    text = f'{await last_block()}'
    await bot.edit_message_text(text=text, chat_id=chat_id, message_id=wait_id, parse_mode='HTML')
    await bot.send_chat_action(chat_id, types.ChatActions.UPLOAD_DOCUMENT)
    await asyncio.sleep(1)
    await bot.send_document(chat_id=chat_id, document=open('transactions.html', 'rb'), reply_markup=menu_keyboard)


@logger.catch
@dispatcher.message_handler(commands='exchange')
@dispatcher.throttled(anti_flood, rate=3)
async def exchange_handler(message: types.Message):
    """Хэндлер команды /exchange"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    message_id = message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=message_id)
    loguru.logger.info(
        f"Введена команда /exchange пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    await bot.send_sticker(chat_id=chat_id,
                           sticker=exchange_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    text = f'{await cryptocurrency_exchange_rate()}'
    await bot.send_message(chat_id, text=text, parse_mode='HTML', reply_markup=menu_keyboard)


@logger.catch
@dispatcher.message_handler(commands='block')
@dispatcher.throttled(anti_flood, rate=3)
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
        wait_id = (
            await bot.send_message(chat_id, '⚙️ <b>Подготавливаем данные, это может занять некоторое время...</b>',
                                   parse_mode='HTML')).message_id
        await bot.edit_message_text(text=text, chat_id=chat_id, message_id=wait_id, parse_mode='HTML')
        if text != '❌ Введен неверный ID блока!':
            await bot.send_chat_action(chat_id, types.ChatActions.UPLOAD_DOCUMENT)
            await asyncio.sleep(1)
            await bot.send_document(chat_id=chat_id, document=open('transactions.html', 'rb'),
                                    reply_markup=menu_keyboard)
        else:
            await bot.delete_message(chat_id=chat_id, message_id=stickwel_id)
    except:
        stick_id = (await bot.send_sticker(chat_id=chat_id,
                                           sticker=block_sticker)).message_id
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await Form.block_id.set()
        msgg_id = (await message.reply("Введите идентификатор блока:")).message_id


@dispatcher.message_handler(state=Form.block_id)
@dispatcher.throttled(anti_flood, rate=3)
async def process_block_id(message: types.Message, state: FSMContext):
    """
    Обработка ID Блока
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
    wait_id = (await bot.send_message(chat_id, '⚙️ <b>Подготавливаем данные, это может занять некоторое время...</b>',
                                      parse_mode='HTML')).message_id
    await bot.edit_message_text(text=text, chat_id=chat_id, message_id=wait_id, parse_mode='HTML')
    if text != '❌ Введен неверный ID блока!':
        await bot.send_chat_action(chat_id, types.ChatActions.UPLOAD_DOCUMENT)
        await asyncio.sleep(1)
        await bot.send_document(chat_id=chat_id, document=open('transactions.html', 'rb'), reply_markup=menu_keyboard)
    else:
        await bot.delete_message(chat_id=chat_id, message_id=stickwel_id)


@logger.catch
@dispatcher.message_handler(commands='balance')
@dispatcher.throttled(anti_flood, rate=3)
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
@dispatcher.throttled(anti_flood, rate=3)
async def process_addr(message: types.Message, state: FSMContext):
    """
    Обработка BTC адресса
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
@dispatcher.throttled(anti_flood, rate=3)
@dispatcher.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
    """Закрытие state в случае ввода /cancel"""
    loguru.logger.info("Ожидание ввода данных прервано командой /cancel")
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await message.reply('Отменено')


@dispatcher.callback_query_handler(CallbackDataFilter(data='last'))
@dispatcher.throttled(anti_flood, rate=10)
async def process_callback_last(callback_query: CallbackQuery):
    """Хэндлер команды /last"""
    loguru.logger.info("Нажата кнопка последнего блока пользователем")
    chat_id = callback_query.message.chat.id
    await bot.send_sticker(chat_id=chat_id,
                           sticker=last_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    wait_id = (await bot.send_message(chat_id, '⚙️ <b>Подготавливаем данные, это может занять некоторое время...</b>',
                                      parse_mode='HTML')).message_id
    text = f'{await last_block()}'
    await bot.edit_message_text(text=text, chat_id=chat_id, message_id=wait_id, parse_mode='HTML')
    await bot.send_chat_action(chat_id, types.ChatActions.UPLOAD_DOCUMENT)
    await asyncio.sleep(1)
    await bot.send_document(chat_id=chat_id, document=open('transactions.html', 'rb'), reply_markup=menu_keyboard)


@dispatcher.callback_query_handler(CallbackDataFilter(data='exchange'))
@dispatcher.throttled(anti_flood, rate=10)
async def process_callback_exchange(callback_query: CallbackQuery):
    """CallbackDataFilter кнопки exchange"""
    loguru.logger.info("Нажата кнопка курс BTC пользователем")
    chat_id = callback_query.message.chat.id
    user_id = callback_query.message.from_user.id
    await bot.send_sticker(chat_id=chat_id,
                           sticker=exchange_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    text = f'{await cryptocurrency_exchange_rate()}'
    await bot.send_message(chat_id, text=text, parse_mode='HTML', reply_markup=menu_keyboard)


@dispatcher.callback_query_handler(CallbackDataFilter(data='block'))
@dispatcher.throttled(anti_flood, rate=10)
async def process_callback_block(callback_query: CallbackQuery):
    """CallbackDataFilter кнопки block"""
    loguru.logger.info("Нажата кнопка блок пользователем")
    chat_id = callback_query.message.chat.id
    global msgg_id, stick_id, stickwel_id
    stick_id = (await bot.send_sticker(chat_id=chat_id,
                                       sticker=block_sticker)).message_id
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await Form.block_id.set()
    message = await bot.send_message(callback_query.from_user.id, "Введите идентификатор блока:")
    msgg_id = message.message_id


@dispatcher.callback_query_handler(CallbackDataFilter(data='balance'))
@dispatcher.throttled(anti_flood, rate=10)
async def process_callback_balance(callback_query: CallbackQuery):
    """CallbackDataFilter кнопки balance"""
    loguru.logger.info("Нажата кнопка баланс пользователем")
    chat_id = callback_query.message.chat.id
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
@dispatcher.throttled(anti_flood, rate=10)
async def process_callback_menu(callback_query: CallbackQuery):
    """CallbackDataFilter кнопки меню"""
    chat_id = callback_query.message.chat.id
    loguru.logger.info("Нажата кнопка меню пользователем")
    await bot.send_sticker(chat_id=chat_id, sticker=menu_sticker)
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await bot.send_message(chat_id=chat_id, text=menu, parse_mode='HTML', reply_markup=start_menu)


@dispatcher.message_handler(commands='subscribe')
@dispatcher.throttled(anti_flood, rate=3)
async def subscribe_handler(message: types.Message):
    """Хэндлер команды /subscribe"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    msg_id = message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    loguru.logger.info(
        f"Введена команда /subscribe пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    if is_in_db(chat_id):
        await bot.send_sticker(chat_id, error_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await bot.send_message(chat_id=chat_id, text='❌ Подписка уже оформлена', parse_mode='HTML',
                               reply_markup=menu_keyboard)
    else:
        conn = sqlite3.connect('dbs/subscribers.db')  # подключение к базе данных
        c = conn.cursor()

        c.execute('CREATE TABLE IF NOT EXISTS subscribers (chat_id INTEGER)')  # создание таблицы
        c.execute('INSERT INTO subscribers (chat_id) VALUES (?)',
                  (chat_id,))  # добавление в столбец id значения user_id

        conn.commit()
        conn.close()
        await bot.send_sticker(chat_id, sub_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        loguru.logger.info(f"Новая подписка на рассылку: ID{chat_id}")
        await bot.send_message(chat_id=chat_id, text='✅ Подписка успешно оформлена', parse_mode='HTML',
                               reply_markup=menu_keyboard)


@dispatcher.message_handler(commands='unsubscribe')
@dispatcher.throttled(anti_flood, rate=3)
async def unsubscribe_handler(message: types.Message):
    """Хэндлер команды /unsubscribe"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    msg_id = message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    loguru.logger.info(
        f"Введена команда /unsubscribe пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    if is_in_db(chat_id):
        conn = sqlite3.connect('dbs/subscribers.db')
        c = conn.cursor()

        c.execute("DELETE FROM subscribers WHERE chat_id=?", (chat_id,))

        conn.commit()
        conn.close()
        await bot.send_sticker(chat_id, unsub_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await bot.send_message(chat_id=chat_id, text='✅ Подписка отменена', parse_mode='HTML',
                               reply_markup=menu_keyboard)
    else:
        await bot.send_sticker(chat_id, error_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await bot.send_message(chat_id=chat_id, text='❌ Вы еще не оформляли подписку', parse_mode='HTML',
                               reply_markup=menu_keyboard)


@dispatcher.message_handler(commands='watch')
@dispatcher.throttled(anti_flood, rate=3)
async def watch_handler(message: types.Message):
    """Хэндлер команды /watch"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    msg_id = message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    loguru.logger.info(
        f"Введена команда /watch пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    global msgg_id, stick_id, stickwel_id
    stick_id = (await bot.send_sticker(chat_id=chat_id,
                                       sticker=block_sticker)).message_id
    await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
    await Form.watch_addr.set()
    message = await bot.send_message(chat_id, "Введите кошелек для отслеживания:")
    msgg_id = message.message_id


@dispatcher.message_handler(state=Form.watch_addr)
@dispatcher.throttled(anti_flood, rate=3)
async def process_watch(message: types.Message, state: FSMContext):
    """
    Обработка адресса для отслеживания
    """
    chat_id = message.chat.id
    msg_id = message.message_id

    async with state.proxy() as data:
        data['watch_addr'] = message.text
        await state.finish()

    watch_addr = data['watch_addr']
    await bot.delete_message(chat_id=chat_id, message_id=stick_id)
    await bot.delete_message(chat_id=chat_id, message_id=msgg_id)
    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    if wallet_in_db(chat_id):
        await bot.send_sticker(chat_id, error_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await bot.send_message(chat_id=chat_id, text='❌ Подписка уже оформлена', parse_mode='HTML',
                               reply_markup=menu_keyboard)
    else:
        conn = sqlite3.connect('dbs/subscribers.db')  # подключение к базе данных
        c = conn.cursor()

        c.execute('CREATE TABLE IF NOT EXISTS wallet_watcher (chat_id INTEGER, wallet TEXT, balance TEXT)')  # создание таблицы
        c.execute(
            'INSERT INTO wallet_watcher (chat_id, wallet, balance) VALUES (?, ?, ?)',
            (chat_id, watch_addr, btc_adress_change(watch_addr)),
        )

        conn.commit()
        conn.close()
        await bot.send_sticker(chat_id, sub_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        loguru.logger.info(f"Новая подписка на отслеживание баланса криптокошелька: ID{chat_id}")
        await bot.send_message(chat_id=chat_id, text='✅ Подписка успешно оформлена', parse_mode='HTML',
                               reply_markup=menu_keyboard)


@dispatcher.message_handler(commands='unwatch')
@dispatcher.throttled(anti_flood, rate=3)
async def watch_handler(message: types.Message):
    """Хэндлер команды /watch"""
    chat_id = message.chat.id
    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    msg_id = message.message_id
    await bot.delete_message(chat_id=chat_id, message_id=msg_id)
    loguru.logger.info(
        f"Введена команда /unwatch пользователем. Имя: {full_name}, ID: {user_id}, юзернейм: {username}")
    if wallet_in_db(chat_id):
        conn = sqlite3.connect('dbs/subscribers.db')
        c = conn.cursor()

        c.execute("DELETE FROM wallet_watcher WHERE chat_id=?", (chat_id,))

        conn.commit()
        conn.close()
        await bot.send_sticker(chat_id, unsub_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await bot.send_message(chat_id=chat_id, text='✅ Подписка отменена', parse_mode='HTML',
                               reply_markup=menu_keyboard)
    else:
        await bot.send_sticker(chat_id, error_sticker)
        await bot.send_chat_action(chat_id, types.ChatActions.TYPING)
        await bot.send_message(chat_id=chat_id, text='❌ Вы еще не оформляли подписку', parse_mode='HTML',
                               reply_markup=menu_keyboard)
        

# хендлер команды /admin
@dispatcher.message_handler(commands=['admin'])
@dispatcher.throttled(anti_flood, rate=3)
async def admin_menu_handler(message: types.Message):
    # Подключаемся к базе данных
    conn = sqlite3.connect('dbs/users.db')
    cursor = conn.cursor()

    # Создаем таблицу, если ее нет
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (chat_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    # проверяем, является ли пользователь администратором
    if message.from_user.id not in ADMIN_IDS:
        await bot.send_sticker(message.chat.id, error_sticker)
        await message.answer("❌ Извините, вы не являетесь администратором.")
        return

    # отправляем сообщение с инлайн клавиатурой
    await bot.send_sticker(message.chat.id, sub_sticker)
    await message.answer("🛠️ Выберите действие:", reply_markup=admin_inline)


# хендлер для обработки выбора инлайн кнопки
@dispatcher.callback_query_handler(text=['broadcast', 'stats'])
@dispatcher.throttled(anti_flood, rate=10)
async def admin_inline_callback_handler(query: types.CallbackQuery, state: FSMContext):
    if query.data == 'broadcast':
        await bot.answer_callback_query(query.id)
        await bot.send_sticker(query.message.chat.id, waiting_sticker)
        await query.message.answer("💌 Введите текст для рассылки (Имеется поддержка HTML разметки):")
        await BroadcastMessage.Text.set()
    elif query.data == 'stats':
        await bot.answer_callback_query(query.id)
        users_count = get_users_count() # функция для получения количества юзеров
        await bot.send_sticker(query.message.chat.id, waiting_sticker)
        await query.message.answer(f"👥 Количество пользователей: {users_count}")

# функция для отправки сообщения всем юзерам бота
async def broadcast_message(text: str, media: List = None):
    users = get_all_users() # функция для получения всех юзеров бота
    for user in users:
        chat_id = user
        try:
            if media:
                if isinstance(media, list) and all(isinstance(item, tuple) for item in media):
                    # отправляем медиафайлы вместе с сообщением
                    await bot.send_media_group(chat_id=chat_id, media=media, parse_mode='HTML')
                else:
                    logger.error(f"Некорректный список медиафайлов для отправки: {media}")
            if text:
                await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Ошибка при отправке сообщения пользователю {chat_id}: {e}")
            await asyncio.sleep(0.5)


# хендлер для получения текста сообщения для рассылки
@dispatcher.message_handler(state=BroadcastMessage.Text)
@dispatcher.throttled(anti_flood, rate=3)
async def broadcast_text_handler(message: types.Message, state: FSMContext):
    text = message.text
    media = []
    if message.photo:
        media = message.photo
    elif message.video:
        media = message.video
    try:
        await broadcast_message(text, media)
        await state.finish()
        await bot.send_sticker(message.chat.id, sub_sticker)
        await message.answer("✅ Рассылка завершена")
    except Exception as e:
        logger.error(f"Ошибка при рассылке сообщения: {e}")
        await message.answer("❌ Произошла ошибка при рассылке сообщения.")



if __name__ == '__main__':
    # Запуск бота
    executor.start_polling(dispatcher)
