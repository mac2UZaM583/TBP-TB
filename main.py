from settings__ import files_content
from pybit.unified_trading import HTTP
from bot import send_message_to_channel
from itertools import count
from time import sleep
import traceback
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

def main():
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
            sleep(5)
        except:
            traceback.print_exc()
            sleep(5)

if __name__ == '__main__':
    main()
