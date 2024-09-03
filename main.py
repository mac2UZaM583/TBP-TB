from settings__ import files_content
from pybit.unified_trading import HTTP
from bot import send_message_to_channel
from itertools import count
from time import sleep
import traceback
import datetime
import schedule
from pprint import pprint

session = HTTP(
    demo=False if files_content['MODE'].upper() == 'NODEMO' else True,
    api_key=files_content['API_EXCHANGE'],
    api_secret=files_content['API_2_EXCHANGE']
)
counter = count(start=0, step=1)
with open('ORDER_ID.txt', 'r', encoding='utf-8') as f:
    order_id = f.read()

def get_info(position_closed):
    side = position_closed['side']
    entry_price = float(position_closed['avgEntryPrice'])
    exit_price = float(position_closed['avgExitPrice'])
    leverage = float(position_closed['leverage'])
    pnl_percent = round((((exit_price / (entry_price / 100)) - 100) * leverage) * (-1 if side == 'Buy' else 1), 2)
    time = session.get_order_history(category='linear')['result']['list'][0]['updatedTime']
    
    return (
        f"🌍 Ticker: {position_closed['symbol']}\n" 
        f"Leverage: {leverage}\n" 
        f"Side: {side}\n" 
        f"Closed PNL: {position_closed['closedPnl']}\n" 
        f"PNL percent: {pnl_percent}%\n" 
        f"Balance USDT: {round(float(session.get_wallet_balance(
            accountType=files_content['ACCOUNT_TYPE'].upper(), 
            coin='USDT'
        )['result']['list'][0]['coin'][0]['walletBalance']), 2)}\n" 
        f'Time: {time}\n' 
    )

def g_pnl_closed():
    timestamp_ms = int(datetime.datetime.combine(datetime.datetime.now().date(), datetime.time()).timestamp() * 1000)
    pnl_closed_all = []
    cursor = None
    while True:
        pnl_closed = session.get_closed_pnl(
            category='linear', 
            endTime=str(timestamp_ms), 
            startTime=str(timestamp_ms - 86_400_000),
            limit=100,
            cursor=cursor
        )['result']
        cursor = pnl_closed["nextPageCursor"]
        pnl_closed_all.extend(pnl_closed["list"])
        if len(pnl_closed) < 100 and cursor == "":
            return pnl_closed_all

def s_total_info():
    pnl_closed = g_pnl_closed()
    balance = float(session.get_wallet_balance(
        accountType=files_content['ACCOUNT_TYPE'].upper(), 
        coin='USDT'
    )['result']['list'][0]['coin'][0]['walletBalance'])
    balance_ = balance
    success_rate = []
    for pnl in pnl_closed:
        pnl_ = float(pnl["closedPnl"])
        balance_ -= pnl_
        if pnl_ > 0:
            success_rate.append(pnl)
    len_total_orders = len(pnl_closed)
    send_message_to_channel(
        f"📑 Earned: {round(balance - balance_, 3)}$\n"
        f"Percentage of changes: ~{round((balance / balance_ - 1) * 100, 3)}%\n"
        f"Success rate: {round(len(success_rate) / len_total_orders * 100, 3)}%\n"
        f"Total orders: {len_total_orders}\n"
        f"Balance: {round(balance, 3)}$"
    )

def main():
    schedule.every().day.at("00:02").do(s_total_info)
    while True:
        try:
            print(next(counter))
            position_closed = session.get_closed_pnl(category='linear', page=1)['result']['list'][0]
            order_id_position = position_closed['orderId']
            global order_id
            if order_id_position != order_id:
                send_message_to_channel(get_info(position_closed))            
                with open('ORDER_ID.txt', 'w', encoding='utf-8') as f:
                    f.write(order_id_position)
                with open('ORDER_ID.txt', 'r', encoding='utf-8') as f:
                    order_id = f.read()
            schedule.run_pending()
            sleep(5)
        except:
            traceback.print_exc()
            sleep(5)

if __name__ == '__main__':
    main()
    # s_total_info()