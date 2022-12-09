import requests
import json
from blockcypher import get_block_overview
import datetime
import base58

# курс крипты
r = requests.get('https://www.blockchain.com/ru/ticker').json()

print(f"BUY: {r['RUB']['buy']} {r['RUB']['symbol']}\nSELL: {r['RUB']['sell']} {r['RUB']['symbol']}")

# -----------------------------------------------------------

# последний блок
last_block = requests.get(url=f'https://api.bitaps.com/btc/v1/blockchain/block/last').json()
block = last_block['data']['hash']
block_info = get_block_overview(block)

# время блока
date_str = str(block_info['time'])
msk = str(block_info['time'])
msk = msk.split(' ')[1].split(':')[0]
msk = int(msk)
msk += 3

print(
    f'Block hash: {block_info["hash"]}\nHeight: {block_info["height"]}\nChain: {block_info["chain"]}\nNonce: {block_info["nonce"]}\nRelated by: {block_info["relayed_by"]}\nBits: {block_info["bits"]}\nTime: {date_str.split(" ")[0]} {msk}:{date_str.split(":")[1]}')

# -----------------------------------------------------------

# блоки
block_id = input('Input Block ID: ')

b = requests.get(url=f'https://api.bitaps.com/btc/v1/blockchain/block/{block_id}').json()
block_hash = b['data']['hash']
block_info = get_block_overview(block_hash)

# время блока
date_str = str(block_info['time'])
msk = str(block_info['time'])
msk = msk.split(' ')[1].split(':')[0]
msk = int(msk)
msk += 3

print(
    f'Block hash: {block_info["hash"]}\nHeight: {block_info["height"]}\nChain: {block_info["chain"]}\nNonce: {block_info["nonce"]}\nRelated by: {block_info["relayed_by"]}\nBits: {block_info["bits"]}\nTime: {date_str.split(" ")[0]} {msk}:{date_str.split(":")[1]}')

for i in range(len(block_info['txids'])):
    tx = requests.get(url=f"https://blockchain.info/rawtx/{block_info['txids'][i]}").json()
    # сумма
    sums = tx['out']
    sums = int(str(sums).split("'value': ")[1].split(", 'spending_outpoints'")[0])
    sums /= 100000000

    # сумма в рублях
    r = requests.get('https://www.blockchain.com/ru/ticker').json()
    sum_rub = sums * r['RUB']['buy']

    # получатель
    receiver = str(tx['out']).split("'addr': '")[1].split("'}")[0]

    # потрачены ли
    spent = str(tx['out']).split("'spent': ")[1].split(", 'value': ")[0]
    if spent == 'False':
        spent = 'Нет'
    else:
        spent = 'Да'

    print(f'Хеш: {tx["hash"]}\nСумма: {sums} BTC ({sum_rub} RUB)\nПотрачены ли: {spent}\nКому: {receiver}')

# -----------------------------------------------------------

# баланс кошелька
addr = input('Enter BTC address: ')

one_btc_balance = requests.get(f'https://blockchain.info/rawaddr/{addr}').json()

# скрытие части адреса
hidden_addr = str(addr[:-12]) + '************'

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

print(f'Хеш-160: {one_btc_balance["hash160"]}\nАдрес: {hidden_addr}\nВсего получено: {total_received} BTC ({total_received_rub} RUB)\nВсего отправлено: {total_sent} BTC ({total_sent_rub} RUB)\nИтоговый баланс: {final_balance} BTC ({final_balance_rub} RUB)')
