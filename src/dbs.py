import sqlite3

def get_all_users():
    conn = sqlite3.connect('dbs/users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_users_count():
    conn = sqlite3.connect('dbs/users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count


# Проверка есть ли юзер в базе данных
def is_in_db(chat_id):
    conn = sqlite3.connect('dbs/subscribers.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS subscribers (chat_id INTEGER)')
    cursor.execute("SELECT * FROM subscribers WHERE chat_id=?", (chat_id,))
    rows = cursor.fetchone()
    return rows is not None


# Проверка есть ли юзер в базе данных
def wallet_in_db(chat_id):
    conn = sqlite3.connect('dbs/subscribers.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS wallet_watcher (chat_id INTEGER, wallet TEXT, balance TEXT)')  # создание таблицы
    cursor.execute("SELECT * FROM wallet_watcher WHERE chat_id=?", (chat_id,))
    
    rows = cursor.fetchone()
    return rows is not None


# Поиск адреса кошелька в базе данных
def get_wallet(chat_id):
    conn = sqlite3.connect('dbs/subscribers.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS wallet_watcher (chat_id INTEGER, wallet TEXT, balance TEXT)')
    cursor.execute("SELECT wallet FROM wallet_watcher WHERE chat_id=?", (chat_id,))

    subscribers = cursor.fetchone()
    return subscribers[0] if subscribers is not None else None


# Поиск даты последней проверки в базе данных
def get_last_check(chat_id):
    conn = sqlite3.connect('dbs/subscribers.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS wallet_watcher (chat_id INTEGER, wallet TEXT, balance TEXT)')  # создание таблицы
    cursor.execute("SELECT date FROM wallet_watcher WHERE chat_id=?", (chat_id,))
    
    subscribers = cursor.fetchone()
    return subscribers[0] if subscribers is not None else None


# Получение старого баланса
def get_old_balance(chat_id):
    conn = sqlite3.connect('dbs/subscribers.db')
    cursor = conn.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS wallet_watcher (chat_id INTEGER, wallet TEXT, balance TEXT)')  # создание таблицы
    cursor.execute("SELECT balance FROM wallet_watcher WHERE chat_id=?", (chat_id,))
    
    subscribers = cursor.fetchone()
    return subscribers[0] if subscribers is not None else None


def parse_from_base():
    # connect to the database
    conn = sqlite3.connect('dbs/subscribers.db')

    # create cursor object
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS subscribers (chat_id INTEGER)')
    # Select all the rows from the table
    c.execute("SELECT chat_id FROM subscribers")

    # Fetch all the results from the table
    global subscribers
    subscribers = c.fetchall()
    subscribers = [i[0] for i in subscribers]
    c.close()
    conn.close()


def parse_from_base_wallet():
    # connect to the database
    conn = sqlite3.connect('dbs/subscribers.db')

    # create cursor object
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS wallet_watcher (chat_id INTEGER, wallet TEXT, balance TEXT)')  # создание таблицы
    # Select all the rows from the table
    c.execute("SELECT chat_id FROM wallet_watcher")

    # Fetch all the results from the table
    subscribers = c.fetchall()
    subscribers = [i[0] for i in subscribers]
    c.close()
    conn.close()
    return subscribers


def create_users_table():
    # Подключаемся к базе данных
    conn = sqlite3.connect('dbs/users.db')
    cursor = conn.cursor()

    # Создаем таблицу, если ее нет
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (chat_id INTEGER PRIMARY KEY)''')
    conn.commit()
    conn.close()
