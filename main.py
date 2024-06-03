from pybit.unified_trading import HTTP
from keys import api_key, api_secret
from bot import send_message_to_channel
import time

session = HTTP(
    demo=True,
    api_key=api_key,
    api_secret=api_secret
)

n = 0
posNum = 3
orderId_copy = [False]

while True:
    try:
        n += 1
        print(f'Запрос номер {n}')
        closedPnlPos = session.get_closed_pnl(category='linear', page=1)['result']['list'][0]
        orderId = closedPnlPos['orderId']
        
        if orderId != orderId_copy[0]:
            orderId_copy.clear()
            posNum += 1
            orderId_copy.append(orderId)
            EntryPrice = float(closedPnlPos['avgEntryPrice'])
            ExitPrice = float(closedPnlPos['avgExitPrice'])
            Leverage = int(closedPnlPos['leverage'])
            balance_info = session.get_wallet_balance(accountType='UNIFIED', coin='USDT')
            wallet_balance = round(float(balance_info['result']['list'][0]['coin'][0]['walletBalance']), 2)
            pnl_percent = -round((((EntryPrice / ExitPrice) * 100) - 100) * Leverage, 2)

            Messege = (
                f"🌍 Ticker: {closedPnlPos['symbol']}\n"
                f"Leverage: {Leverage}\n"
                f"Side: {closedPnlPos['side']}\n"
                f"ClosedPnl: {closedPnlPos['closedPnl']}\n"
                f"BalanceUSDT: {wallet_balance}\n"
                f"EntryPrice: {EntryPrice}\n"
                f"ExitPrice: {ExitPrice}\n"
                f"PnlPercent: {pnl_percent}%\n"
                f"PositionTestNumber: {posNum}"
                )
            
            send_message_to_channel(Messege)
            print(f"Сообщение отправлено в канал! \nСообщение: \n{Messege}")

        time.sleep(5)
    except Exception as er:
        print(er)