from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

'''Inline-клавиатуры'''
# Создание кнопок для основной клавиатуры
button_last = InlineKeyboardButton('🔍 Последний блок', callback_data='last')
button_exchange = InlineKeyboardButton('💰 Курс Биткоина', callback_data='exchange')
button_block = InlineKeyboardButton('🔗 Информация о блоке', callback_data='block')
button_balance = InlineKeyboardButton('💼 Биткоин кошелек', callback_data='balance')

# создаем инлайн клавиатуру с двумя кнопками
admin_inline = InlineKeyboardMarkup(row_width=2)
admin_inline.insert(InlineKeyboardButton("Рассылка", callback_data='broadcast'))
admin_inline.insert(InlineKeyboardButton("Статистика", callback_data='stats'))

# Создание основной клавиатуры и внесение в нее кнопок
start_menu = InlineKeyboardMarkup()
start_menu.add(button_last)
start_menu.add(button_exchange)
start_menu.add(button_block)
start_menu.add(button_balance)

# Создание клавиатуры, для перенаправления в меню
menu_keyboard = InlineKeyboardMarkup()
menu_button_text = InlineKeyboardButton('◀️ В меню', callback_data='menu')
menu_keyboard.add(menu_button_text)

# Стикеры бота (вынесены для удобного редактирования)
menu_sticker = 'CAACAgIAAxkBAAEHi25j2o75xyB-m8C3s4ITgCo7JWPEmQACph8AAv0RsEpbI3U8YSp1vy4E'
last_sticker = 'CAACAgIAAxkBAAEHi4Nj2pISiR7ub3J2ZJoFKgpZLkCFagACKCkAAtjzqErya_sR6K2N4i4E'
exchange_sticker = 'CAACAgIAAxkBAAEHi4Vj2pI1uvDP9bz6NoJuw0kX9rz7tQAC7i4AAu6RsEpU_iAgu_9-aS4E'
block_sticker = 'CAACAgIAAxkBAAEHi4lj2pJS89tE80V_ZHZuAc2G046hYAACGSsAAgREqErosNZKKuXTDC4E'
balance_sticker = 'CAACAgIAAxkBAAEHi5Zj2pUrlw0OKm70CCTKPpUB9KqN9gACVyUAAsoEqUp6NgKY6HXb-S4E'
error_sticker = 'CAACAgIAAxkBAAEHi5Fj2pUO7WE5dh8RaOOAzL-5LslsIAACkCwAAvLrqUr7GbPrm5Xk9C4E'
sub_sticker = 'CAACAgIAAxkBAAEHlDRj3WaudkWdYnI_-i9weZA5InsLWwACtSkAAnIHsEpATn7qYGoMBS4E'
unsub_sticker = 'CAACAgIAAxkBAAEHlDZj3WbOv1Q5yN9stdn_z42jDyEQXwACkCwAAvLrqUr7GbPrm5Xk9C4E'
waiting_sticker = 'CAACAgIAAxkBAAEIDN9kCIPRjO59aCW5aneZa7pNGK8eTQACICcAAshksUp3QmT3Zh9l-y4E'

# Переменная меню (вынесена для быстрого редактирования)
menu = '''
🔥 <b>Меню:</b>

💰 <b>Курс Биткоина:</b> Получите актуальный курс Биткоина на Blockchain
🔍 <b>Последний блок:</b> Получите информацию о последнем блоке в сети Биткоин, включая транзакции
💼 <b>Биткоин кошелек:</b> Получите информацию о вашем Биткоин кошельке, включая баланс, общую сумму поступлений и выводов
🔗 <b>Информация о блоке:</b> Получите информацию о конкретном блоке по его номеру
'''
