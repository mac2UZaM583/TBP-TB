from pybit.unified_trading import HTTP
from keys import api_key, api_secret
from bot import send_message_to_channel
import itertools
import time
from datetime import datetime
import traceback

session = HTTP(
    # demo=True,
    api_key=api_key,
    api_secret=api_secret
)

counter = itertools.count(start=0, step=1)
with open('orderId.txt', 'r', encoding='utf-8') as f:
    orderId_copy = [f.read()]

def get_info(closed_pnl_pos):
    entry_price = float(closed_pnl_pos['avgEntryPrice'])
    exit_price = float(closed_pnl_pos['avgExitPrice'])
    leverage = float(closed_pnl_pos['leverage'])
    balance_info = session.get_wallet_balance(accountType='CONTRACT', coin='USDT')
    wallet_balance = round(float(balance_info['result']['list'][0]['coin'][0]['walletBalance']), 2)
    pnl_percent_none = round((((entry_price / exit_price) * 100) - 100) * leverage, 2)
    pnl_percent = -pnl_percent_none if closed_pnl_pos['side'] == 'Sell' else pnl_percent_none
    time = session.get_order_history(category='linear')['result']['list'][0]['updatedTime']    
    return (closed_pnl_pos['symbol'], 
            leverage, 
            closed_pnl_pos['side'], 
            closed_pnl_pos['closedPnl'], 
            wallet_balance, 
            entry_price, 
            exit_price, 
            pnl_percent,
            time)

def get_messege(symbol, leverage, side, closed_pnl, wallet_balance, entry_price, exit_price, pnl_percent, time, position_num):
    messege = (f"🌍 Ticker: {symbol}\n" 
               f"Leverage: {leverage}\n" 
               f"Side: {side}\n" 
               f"Closed PNL: {closed_pnl}\n" 
               f"Balance USDT: {wallet_balance}\n" 
               f"Entry price: {entry_price}\n" 
               f"Exit price: {exit_price}\n" 
               f"PNL percent: {pnl_percent}%\n" 
               f'Time: {time}\n' 
               f"Position number: {position_num}")
    return messege

def save(position_num, order_id):
    with open('posNum.txt', 'w', encoding='utf-8') as f:
        f.write(position_num)
    with open('orderId.txt', 'w', encoding='utf-8') as f:
        f.write(order_id)

def main():
    while True:
        try:
            '''PRE ↓
            '''
            print(f'Запрос {next(counter)}')
            closed_pnl_pos = session.get_closed_pnl(category='linear', page=1)['result']['list'][0]
            order_id = closed_pnl_pos['orderId']

            '''POST ↓
            '''
            if order_id != orderId_copy[0]:
                with open('posNum.txt', 'r', encoding='utf-8') as f:
                    position_num = int(f.read())
                orderId_copy.clear()
                position_num = str(position_num + 1)
                orderId_copy.append(order_id)
                info = get_info(closed_pnl_pos=closed_pnl_pos)
                messege = get_messege(*info, position_num=position_num)
                send_message_to_channel(messege)
                save(position_num=position_num, order_id=order_id)
                print(f"Сообщение отправлено в канал! \nСообщение: \n{messege}")
            
            time.sleep(5)
        except:
            traceback.print_exc()
            time.sleep(5)

if __name__ == '__main__':
    main()
