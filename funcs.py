import requests
from blockcypher import get_block_overview
import asyncio
import json


def load_file(file_path):
    """
    It uploads a file to a file sharing service and returns the link to the uploaded file
    
    :param file_path: The path to the file you want to upload
    :return: The link to the file on the file sharing service.
    """
    files = {
        'f': open(f'{file_path}', 'rb'),
        'randomizefn': (None, '1'),
        'shorturl': (None, '0'),
    }

    chat_id = '1074797971'
    API_TOKEN = ''

    try:
        r = requests.post('https://oshi.at', files=files)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        requests.get(f'https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={chat_id}&text=❗️ Ошибка при загрузке файла на файлообменник: {e}')
        return None
    
    return r.text.splitlines()[1].split()[1]

    


async def cryptocurrency_exchange_rate():
    """
    It takes the JSON response from the API and returns a string with the buy and sell prices
    :return: The return value is a string.
    """
    # курс крипты
    global r
    r = requests.get('https://www.blockchain.com/ru/ticker').json()
    return f"💰 <b>Покупка</b>: <code>{r['RUB']['buy']} {r['RUB']['symbol']}</code>\n💸 <b>Продажа</b>: <code>{r['RUB']['sell']} {r['RUB']['symbol']}</code>"


# -----------------------------------------------------------


async def last_block():
    """
    It gets the last block, gets the transactions in that block, and writes them to a file.
    :return: The return value is a string.
    """
    # последний блок
    global block_info, date_str, msk
    last_block = requests.get(
        url='https://api.bitaps.com/btc/v1/blockchain/block/last'
    ).json()
    block = last_block['data']['hash']
    block_info = get_block_overview(block)

    # время блока
    date_str = str(block_info['time'])
    msk = str(block_info['time'])
    msk = msk.split(' ')[1].split(':')[0]
    msk = int(msk) + 3
    txs_10_ident = 1
    with open('transactions.txt', 'w', encoding='utf-8') as tx_full:
        with open('10_txs.txt', 'w', encoding='utf-8') as txs_10:
            for i in range(len(block_info['txids'])):
                tx = requests.get(url=f"https://blockchain.info/rawtx/{block_info['txids'][i]}").json()

                # сумма
                sums = tx['out']
                sums = (
                    int(
                        str(sums)
                        .split("'value': ")[1]
                        .split(", 'spending_outpoints'")[0]
                    )
                    / 100000000
                )
                # сумма в рублях
                r = requests.get('https://www.blockchain.com/ru/ticker').json()
                sum_rub = sums * r['RUB']['buy']
                sum_rub = round(sum_rub, 2)

                # получатель
                receiver = str(tx['out']).split("'addr': '")[1].split("'}")[0]

                # потрачены ли
                spent = str(tx['out']).split("'spent': ")[1].split(", 'value': ")[0]
                spent = 'Нет' if spent == 'False' else 'Да'
                # Запись в файл с полнимы данными (для юзера)
                tx_full.write(
                    f'Хеш: {tx["hash"]}\nСумма: {sums} BTC ({sum_rub} RUB)\nПотрачены ли: {spent}\nКому: https://www.blockchain.com/explorer/addresses/btc/{receiver}\n\n')
                if txs_10_ident <= 10:
                    # Первые 10 транзакций
                    txs_10.write(
                        f'{spent}|1|<a href="https://www.blockchain.com/explorer/addresses/btc/{receiver}">{receiver}</a>|2|{sums} BTC ({sum_rub} RUB)\n')
                    txs_10_ident += 1

    # генератор HTML

    # открытие файла с 10 транзакциями

    txs_10_read = open('10_txs.txt', 'r')
    mask = open('mask.html', 'r', encoding='cp1251')
    mask_temp = mask.readlines()
    mask_all = ''.join(mask_temp)

    # tx1
    templine = txs_10_read.readline()
    spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
    receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
    sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

    # tx2
    templine = txs_10_read.readline()
    spent2 = sums1.replace('spent2', templine.split('|1|')[0])
    receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
    sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

    # tx3
    templine = txs_10_read.readline()
    spent3 = sums2.replace('spent3', templine.split('|1|')[0])
    receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
    sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

    # tx4
    templine = txs_10_read.readline()
    spent4 = sums3.replace('spent4', templine.split('|1|')[0])
    receiver4 = spent4.replace('receiver4', templine.split('|1|')[1].split('|2|')[0])
    sums4 = receiver4.replace('sums4', templine.split('|2|')[1])

    # tx5
    templine = txs_10_read.readline()
    spent5 = sums4.replace('spent5', templine.split('|1|')[0])
    receiver5 = spent5.replace('receiver5', templine.split('|1|')[1].split('|2|')[0])
    sums5 = receiver5.replace('sums5', templine.split('|2|')[1])

    # tx6
    templine = txs_10_read.readline()
    spent6 = sums5.replace('spent6', templine.split('|1|')[0])
    receiver6 = spent6.replace('receiver6', templine.split('|1|')[1].split('|2|')[0])
    sums6 = receiver6.replace('sums6', templine.split('|2|')[1])

    # tx7
    templine = txs_10_read.readline()
    spent7 = sums6.replace('spent7', templine.split('|1|')[0])
    receiver7 = spent7.replace('receiver7', templine.split('|1|')[1].split('|2|')[0])
    sums7 = receiver7.replace('sums7', templine.split('|2|')[1])

    # tx8
    templine = txs_10_read.readline()
    spent8 = sums7.replace('spent8', templine.split('|1|')[0])
    receiver8 = spent8.replace('receiver8', templine.split('|1|')[1].split('|2|')[0])
    sums8 = receiver8.replace('sums8', templine.split('|2|')[1])

    # tx9
    templine = txs_10_read.readline()
    spent9 = sums8.replace('spent9', templine.split('|1|')[0])
    receiver9 = spent9.replace('receiver9', templine.split('|1|')[1].split('|2|')[0])
    sums9 = receiver9.replace('sums9', templine.split('|2|')[1])

    # tx10
    templine = txs_10_read.readline()
    spent10 = sums9.replace('spent10', templine.split('|1|')[0])
    receiver10 = spent10.replace('receiver10', templine.split('|1|')[1].split('|2|')[0])
    sums10 = receiver10.replace('sums10', templine.split('|2|')[1])

    # link
    done = sums10.replace('linktofile', load_file('transactions.txt'))

    with open('transactions.html', 'w', encoding='cp1251') as txs_report:
        txs_report.write(done)

    return f'🔢 <b>Хеш блока</b>: <code>{block_info["hash"]}</code>\n🌍 <b>Сеть</b>: <code>{block_info["chain"]}</code>\n🔢 <b>Nonce</b>: <code>{block_info["nonce"]}</code>\n📡 <b>Кем создан</b>: <code>{block_info["relayed_by"]}</code>\n⛓️ <b>Биты</b>: <code>{block_info["bits"]}</code>\n🕰️ <b>Время</b>: <code>{date_str.split(" ")[0]} {msk}:{date_str.split(":")[1]}</code>'


# -----------------------------------------------------------


async def block_by_number(block_id):
    # блоки
    global block_info, date_str, msk
    b = requests.get(url=f'https://api.bitaps.com/btc/v1/blockchain/block/{block_id}').json()
    try:
        block_hash = b['data']['hash']

        block_info = get_block_overview(block_hash)

        # время блока
        date_str = str(block_info['time'])
        msk = str(block_info['time'])
        msk = msk.split(' ')[1].split(':')[0]
        msk = int(msk)
        msk += 3

        txs_10_ident = 1
        with open(f'transactions.txt', 'w', encoding='utf-8') as tx_full:
            with open(f'10_txs.txt', 'w', encoding='utf-8') as txs_10:
                for i in range(len(block_info['txids'])):
                    tx = requests.get(url=f"https://blockchain.info/rawtx/{block_info['txids'][i]}").json()

                    # сумма
                    sums = tx['out']
                    sums = int(str(sums).split("'value': ")[1].split(", 'spending_outpoints'")[0])
                    sums /= 100000000

                    # сумма в рублях
                    r = requests.get('https://www.blockchain.com/ru/ticker').json()
                    sum_rub = sums * r['RUB']['buy']
                    sum_rub = round(sum_rub, 2)

                    # получатель
                    receiver = str(tx['out']).split("'addr': '")[1].split("'}")[0]

                    # потрачены ли
                    spent = str(tx['out']).split("'spent': ")[1].split(", 'value': ")[0]
                    if spent == 'False':
                        spent = 'Нет'
                    else:
                        spent = 'Да'

                    # Запись в файл с полнимы данными (для юзера)
                    tx_full.write(
                        f'Хеш: {tx["hash"]}\nСумма: {sums} BTC ({sum_rub} RUB)\nПотрачены ли: {spent}\nКому: https://www.blockchain.com/explorer/addresses/btc/{receiver}\n\n')
                    if txs_10_ident <= 10:
                        # Первые 10 транзакций
                        txs_10.write(
                            f'{spent}|1|<a href="https://www.blockchain.com/explorer/addresses/btc/{receiver}">{receiver}</a>|2|{sums} BTC ({sum_rub} RUB)\n')
                        txs_10_ident += 1

        # генератор HTML

        if sum(1 for line in open('transactions.txt', 'r')) > 50:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'mask.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            # tx3
            templine = txs_10_read.readline()
            spent3 = sums2.replace('spent3', templine.split('|1|')[0])
            receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
            sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

            # tx4
            templine = txs_10_read.readline()
            spent4 = sums3.replace('spent4', templine.split('|1|')[0])
            receiver4 = spent4.replace('receiver4', templine.split('|1|')[1].split('|2|')[0])
            sums4 = receiver4.replace('sums4', templine.split('|2|')[1])

            # tx5
            templine = txs_10_read.readline()
            spent5 = sums4.replace('spent5', templine.split('|1|')[0])
            receiver5 = spent5.replace('receiver5', templine.split('|1|')[1].split('|2|')[0])
            sums5 = receiver5.replace('sums5', templine.split('|2|')[1])

            # tx6
            templine = txs_10_read.readline()
            spent6 = sums5.replace('spent6', templine.split('|1|')[0])
            receiver6 = spent6.replace('receiver6', templine.split('|1|')[1].split('|2|')[0])
            sums6 = receiver6.replace('sums6', templine.split('|2|')[1])

            # tx7
            templine = txs_10_read.readline()
            spent7 = sums6.replace('spent7', templine.split('|1|')[0])
            receiver7 = spent7.replace('receiver7', templine.split('|1|')[1].split('|2|')[0])
            sums7 = receiver7.replace('sums7', templine.split('|2|')[1])

            # tx8
            templine = txs_10_read.readline()
            spent8 = sums7.replace('spent8', templine.split('|1|')[0])
            receiver8 = spent8.replace('receiver8', templine.split('|1|')[1].split('|2|')[0])
            sums8 = receiver8.replace('sums8', templine.split('|2|')[1])

            # tx9
            templine = txs_10_read.readline()
            spent9 = sums8.replace('spent9', templine.split('|1|')[0])
            receiver9 = spent9.replace('receiver9', templine.split('|1|')[1].split('|2|')[0])
            sums9 = receiver9.replace('sums9', templine.split('|2|')[1])

            # tx10
            templine = txs_10_read.readline()
            spent10 = sums9.replace('spent10', templine.split('|1|')[0])
            receiver10 = spent10.replace('receiver10', templine.split('|1|')[1].split('|2|')[0])
            sums10 = receiver10.replace('sums10', templine.split('|2|')[1])

            # link
            done = sums10.replace('linktofile', load_file('transactions.txt'))

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(done))
        elif sum(1 for line in open('10_txs.txt', 'r')) == 10:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            # tx3
            templine = txs_10_read.readline()
            spent3 = sums2.replace('spent3', templine.split('|1|')[0])
            receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
            sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

            # tx4
            templine = txs_10_read.readline()
            spent4 = sums3.replace('spent4', templine.split('|1|')[0])
            receiver4 = spent4.replace('receiver4', templine.split('|1|')[1].split('|2|')[0])
            sums4 = receiver4.replace('sums4', templine.split('|2|')[1])

            # tx5
            templine = txs_10_read.readline()
            spent5 = sums4.replace('spent5', templine.split('|1|')[0])
            receiver5 = spent5.replace('receiver5', templine.split('|1|')[1].split('|2|')[0])
            sums5 = receiver5.replace('sums5', templine.split('|2|')[1])

            # tx6
            templine = txs_10_read.readline()
            spent6 = sums5.replace('spent6', templine.split('|1|')[0])
            receiver6 = spent6.replace('receiver6', templine.split('|1|')[1].split('|2|')[0])
            sums6 = receiver6.replace('sums6', templine.split('|2|')[1])

            # tx7
            templine = txs_10_read.readline()
            spent7 = sums6.replace('spent7', templine.split('|1|')[0])
            receiver7 = spent7.replace('receiver7', templine.split('|1|')[1].split('|2|')[0])
            sums7 = receiver7.replace('sums7', templine.split('|2|')[1])

            # tx8
            templine = txs_10_read.readline()
            spent8 = sums7.replace('spent8', templine.split('|1|')[0])
            receiver8 = spent8.replace('receiver8', templine.split('|1|')[1].split('|2|')[0])
            sums8 = receiver8.replace('sums8', templine.split('|2|')[1])

            # tx9
            templine = txs_10_read.readline()
            spent9 = sums8.replace('spent9', templine.split('|1|')[0])
            receiver9 = spent9.replace('receiver9', templine.split('|1|')[1].split('|2|')[0])
            sums9 = receiver9.replace('sums9', templine.split('|2|')[1])

            # tx10
            templine = txs_10_read.readline()
            spent10 = sums9.replace('spent10', templine.split('|1|')[0])
            receiver10 = spent10.replace('receiver10', templine.split('|1|')[1].split('|2|')[0])
            sums10 = receiver10.replace('sums10', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums10))

        elif sum(1 for line in open('10_txs.txt', 'r')) == 9:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template1.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            # tx3
            templine = txs_10_read.readline()
            spent3 = sums2.replace('spent3', templine.split('|1|')[0])
            receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
            sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

            # tx4
            templine = txs_10_read.readline()
            spent4 = sums3.replace('spent4', templine.split('|1|')[0])
            receiver4 = spent4.replace('receiver4', templine.split('|1|')[1].split('|2|')[0])
            sums4 = receiver4.replace('sums4', templine.split('|2|')[1])

            # tx5
            templine = txs_10_read.readline()
            spent5 = sums4.replace('spent5', templine.split('|1|')[0])
            receiver5 = spent5.replace('receiver5', templine.split('|1|')[1].split('|2|')[0])
            sums5 = receiver5.replace('sums5', templine.split('|2|')[1])

            # tx6
            templine = txs_10_read.readline()
            spent6 = sums5.replace('spent6', templine.split('|1|')[0])
            receiver6 = spent6.replace('receiver6', templine.split('|1|')[1].split('|2|')[0])
            sums6 = receiver6.replace('sums6', templine.split('|2|')[1])

            # tx7
            templine = txs_10_read.readline()
            spent7 = sums6.replace('spent7', templine.split('|1|')[0])
            receiver7 = spent7.replace('receiver7', templine.split('|1|')[1].split('|2|')[0])
            sums7 = receiver7.replace('sums7', templine.split('|2|')[1])

            # tx8
            templine = txs_10_read.readline()
            spent8 = sums7.replace('spent8', templine.split('|1|')[0])
            receiver8 = spent8.replace('receiver8', templine.split('|1|')[1].split('|2|')[0])
            sums8 = receiver8.replace('sums8', templine.split('|2|')[1])

            # tx9
            templine = txs_10_read.readline()
            spent9 = sums8.replace('spent9', templine.split('|1|')[0])
            receiver9 = spent9.replace('receiver9', templine.split('|1|')[1].split('|2|')[0])
            sums9 = receiver9.replace('sums9', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums9))

        elif sum(1 for line in open('10_txs.txt', 'r')) == 8:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template2.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            # tx3
            templine = txs_10_read.readline()
            spent3 = sums2.replace('spent3', templine.split('|1|')[0])
            receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
            sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

            # tx4
            templine = txs_10_read.readline()
            spent4 = sums3.replace('spent4', templine.split('|1|')[0])
            receiver4 = spent4.replace('receiver4', templine.split('|1|')[1].split('|2|')[0])
            sums4 = receiver4.replace('sums4', templine.split('|2|')[1])

            # tx5
            templine = txs_10_read.readline()
            spent5 = sums4.replace('spent5', templine.split('|1|')[0])
            receiver5 = spent5.replace('receiver5', templine.split('|1|')[1].split('|2|')[0])
            sums5 = receiver5.replace('sums5', templine.split('|2|')[1])

            # tx6
            templine = txs_10_read.readline()
            spent6 = sums5.replace('spent6', templine.split('|1|')[0])
            receiver6 = spent6.replace('receiver6', templine.split('|1|')[1].split('|2|')[0])
            sums6 = receiver6.replace('sums6', templine.split('|2|')[1])

            # tx7
            templine = txs_10_read.readline()
            spent7 = sums6.replace('spent7', templine.split('|1|')[0])
            receiver7 = spent7.replace('receiver7', templine.split('|1|')[1].split('|2|')[0])
            sums7 = receiver7.replace('sums7', templine.split('|2|')[1])

            # tx8
            templine = txs_10_read.readline()
            spent8 = sums7.replace('spent8', templine.split('|1|')[0])
            receiver8 = spent8.replace('receiver8', templine.split('|1|')[1].split('|2|')[0])
            sums8 = receiver8.replace('sums8', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums8))

        elif sum(1 for line in open('10_txs.txt', 'r')) == 7:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template3.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            # tx3
            templine = txs_10_read.readline()
            spent3 = sums2.replace('spent3', templine.split('|1|')[0])
            receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
            sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

            # tx4
            templine = txs_10_read.readline()
            spent4 = sums3.replace('spent4', templine.split('|1|')[0])
            receiver4 = spent4.replace('receiver4', templine.split('|1|')[1].split('|2|')[0])
            sums4 = receiver4.replace('sums4', templine.split('|2|')[1])

            # tx5
            templine = txs_10_read.readline()
            spent5 = sums4.replace('spent5', templine.split('|1|')[0])
            receiver5 = spent5.replace('receiver5', templine.split('|1|')[1].split('|2|')[0])
            sums5 = receiver5.replace('sums5', templine.split('|2|')[1])

            # tx6
            templine = txs_10_read.readline()
            spent6 = sums5.replace('spent6', templine.split('|1|')[0])
            receiver6 = spent6.replace('receiver6', templine.split('|1|')[1].split('|2|')[0])
            sums6 = receiver6.replace('sums6', templine.split('|2|')[1])

            # tx7
            templine = txs_10_read.readline()
            spent7 = sums6.replace('spent7', templine.split('|1|')[0])
            receiver7 = spent7.replace('receiver7', templine.split('|1|')[1].split('|2|')[0])
            sums7 = receiver7.replace('sums7', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums7))

        elif sum(1 for line in open('10_txs.txt', 'r')) == 6:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template4.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            # tx3
            templine = txs_10_read.readline()
            spent3 = sums2.replace('spent3', templine.split('|1|')[0])
            receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
            sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

            # tx4
            templine = txs_10_read.readline()
            spent4 = sums3.replace('spent4', templine.split('|1|')[0])
            receiver4 = spent4.replace('receiver4', templine.split('|1|')[1].split('|2|')[0])
            sums4 = receiver4.replace('sums4', templine.split('|2|')[1])

            # tx5
            templine = txs_10_read.readline()
            spent5 = sums4.replace('spent5', templine.split('|1|')[0])
            receiver5 = spent5.replace('receiver5', templine.split('|1|')[1].split('|2|')[0])
            sums5 = receiver5.replace('sums5', templine.split('|2|')[1])

            # tx6
            templine = txs_10_read.readline()
            spent6 = sums5.replace('spent6', templine.split('|1|')[0])
            receiver6 = spent6.replace('receiver6', templine.split('|1|')[1].split('|2|')[0])
            sums6 = receiver6.replace('sums6', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums6))

        elif sum(1 for line in open('10_txs.txt', 'r')) == 5:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template5.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            # tx3
            templine = txs_10_read.readline()
            spent3 = sums2.replace('spent3', templine.split('|1|')[0])
            receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
            sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

            # tx4
            templine = txs_10_read.readline()
            spent4 = sums3.replace('spent4', templine.split('|1|')[0])
            receiver4 = spent4.replace('receiver4', templine.split('|1|')[1].split('|2|')[0])
            sums4 = receiver4.replace('sums4', templine.split('|2|')[1])

            # tx5
            templine = txs_10_read.readline()
            spent5 = sums4.replace('spent5', templine.split('|1|')[0])
            receiver5 = spent5.replace('receiver5', templine.split('|1|')[1].split('|2|')[0])
            sums5 = receiver5.replace('sums5', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums5))

        elif sum(1 for line in open('10_txs.txt', 'r')) == 4:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template6.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            # tx3
            templine = txs_10_read.readline()
            spent3 = sums2.replace('spent3', templine.split('|1|')[0])
            receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
            sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

            # tx4
            templine = txs_10_read.readline()
            spent4 = sums3.replace('spent4', templine.split('|1|')[0])
            receiver4 = spent4.replace('receiver4', templine.split('|1|')[1].split('|2|')[0])
            sums4 = receiver4.replace('sums4', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums4))

        elif sum(1 for line in open('10_txs.txt', 'r')) == 3:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template7.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            # tx3
            templine = txs_10_read.readline()
            spent3 = sums2.replace('spent3', templine.split('|1|')[0])
            receiver3 = spent3.replace('receiver3', templine.split('|1|')[1].split('|2|')[0])
            sums3 = receiver3.replace('sums3', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums3))

        elif sum(1 for line in open('10_txs.txt', 'r')) == 2:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template8.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            # tx2
            templine = txs_10_read.readline()
            spent2 = sums1.replace('spent2', templine.split('|1|')[0])
            receiver2 = spent2.replace('receiver2', templine.split('|1|')[1].split('|2|')[0])
            sums2 = receiver2.replace('sums2', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums2))

        elif sum(1 for line in open('10_txs.txt', 'r')) == 1:
            # открытие файла с 10 транзакциями

            txs_10_read = open(f'10_txs.txt', 'r')
            mask = open(f'template9.html', 'r', encoding='cp1251')
            mask_temp = mask.readlines()
            mask_all = ''.join(mask_temp)

            # tx1
            templine = txs_10_read.readline()
            spent1 = mask_all.replace('spent1', templine.split('|1|')[0])
            receiver1 = spent1.replace('receiver1', templine.split('|1|')[1].split('|2|')[0])
            sums1 = receiver1.replace('sums1', templine.split('|2|')[1])

            with open(f'transactions.html', 'w', encoding='cp1251') as txs_report:
                txs_report.write(str(sums1))

        return f'🔢 <b>Хеш блока</b>: <code>{block_info["hash"]}</code>\n🌍 <b>Сеть</b>: <code>{block_info["chain"]}</code>\n🔢 <b>Nonce</b>: <code>{block_info["nonce"]}</code>\n📡 <b>Кем создан</b>: <code>{block_info["relayed_by"]}</code>\n⛓️ <b>Биты</b>: <code>{block_info["bits"]}</code>\n🕰️ <b>Время</b>: <code>{date_str.split(" ")[0]} {msk}:{date_str.split(":")[1]}</code>'
    except:
        return '❌ Введен неверный ID блока!'


# -----------------------------------------------------------


async def btc_adress_balance(addr):
    """
    It takes a Bitcoin address as input, and returns a string with the balance of that address
    
    :param addr: The address of the wallet you want to check the balance of
    :return: The balance of the wallet
    """
    # баланс кошелька
    global one_btc_balance

    one_btc_balance = requests.get(f'https://blockchain.info/rawaddr/{addr}').json()

    # скрытие части адреса
    hidden_addr = str(addr[:-12]) + '************'

    try:
        # всего получено в рублях
        total_received = int(one_btc_balance["total_received"]) / 100000000
        r = requests.get('https://www.blockchain.com/ru/ticker').json()
        total_received_rub = total_received * r['RUB']['buy']

        # всего отправлено в рублях
        total_sent = int(one_btc_balance["total_sent"]) / 100000000
        r = requests.get('https://www.blockchain.com/ru/ticker').json()
        total_sent_rub = total_sent * r['RUB']['buy']

        # итоговый баланс в рублях
        final_balance = int(one_btc_balance["final_balance"]) / 100000000
        r = requests.get('https://www.blockchain.com/ru/ticker').json()
        final_balance_rub = final_balance * r['RUB']['buy']

        return f'💰 <b>Адрес</b>: <code>{hidden_addr}</code>\n💸 <b>Всего получено</b>: <code>{total_received} BTC ({total_received_rub} RUB</code>)\n💸 <b>Всего отправлено</b>: <code>{total_sent} BTC ({total_sent_rub} RUB)</code>\n💰 <b>Итоговый баланс</b>: <code>{final_balance} BTC ({final_balance_rub} RUB)</code>'
    except:
        return '❌ Введен неверный адрес кошелька!'


# -----------------------------------------------------------


def btc_adress_change(addr):
    """
    It takes a BTC address as an argument, gets the balance of that address, and returns the balance in
    BTC and RUB
    
    :param addr: the address of the wallet
    :return: a string in the format "balance:balance_in_rubles"
    """
    # изменение баланса адреса
    global one_btc_balance

    chat_id = '1074797971'
    API_TOKEN = ''

    try:
        one_btc_balance = requests.get(f'https://blockchain.info/rawaddr/{addr}').json()
    except json.decoder.JSONDecodeError as e:
        # если произошла ошибка декодирования json, отправляем уведомление об ошибке
        requests.get(f'https://api.telegram.org/bot{API_TOKEN}/sendMessage?chat_id={chat_id}&text=❗ Ошибка декодирования JSON в функции btc_adress_change: {e}')

    # итоговый баланс в рублях
    final_balance = int(one_btc_balance["final_balance"]) / 100000000
    r = requests.get('https://www.blockchain.com/ru/ticker').json()
    final_balance_rub = final_balance * r['RUB']['buy']

    return f'{final_balance}:{final_balance_rub}'



# -----------------------------------------------------------

# Старт в дебаг моде, если файл запущен как мейн

# A simple script that uses the blockchain.info API to get information about the current exchange rate
# of Bitcoin, the last block, the block by number, and the balance of the Bitcoin address.
if __name__ == '__main__':
    asyncio.run(cryptocurrency_exchange_rate())
    print(f"Покупка: {r['RUB']['buy']} {r['RUB']['symbol']}\nПродажа: {r['RUB']['sell']} {r['RUB']['symbol']}")
    asyncio.run(last_block())
    print(
        f'Хеш блока: {block_info["hash"]}\nСеть: {block_info["chain"]}\nNonce: {block_info["nonce"]}\nКем создан: {block_info["relayed_by"]}\nБиты: {block_info["bits"]}\nВремя: {date_str.split(" ")[0]} {msk}:{date_str.split(":")[1]}')
    block_id = input('Введите Block ID: ')
    asyncio.run(block_by_number(block_id))
    print(
        f'Хеш блока: {block_info["hash"]}\nСеть: {block_info["chain"]}\nNonce: {block_info["nonce"]}\nКем создан: {block_info["relayed_by"]}\nБиты: {block_info["bits"]}\nВремя: {date_str.split(" ")[0]} {msk}:{date_str.split(":")[1]}')
    addr = input('Введите BTC адрес: ')
    asyncio.run(btc_adress_balance(addr))
    print(
        f'Хеш-160: {one_btc_balance["hash160"]}\nАдрес: {hidden_addr}\nВсего получено: {total_received} BTC ({total_received_rub} RUB)\nВсего отправлено: {total_sent} BTC ({total_sent_rub} RUB)\nИтоговый баланс: {final_balance} BTC ({final_balance_rub} RUB)')
