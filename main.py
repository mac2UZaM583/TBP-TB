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
posNum = 2
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
            Messege = f'🌍 Ticker: {closedPnlPos['symbol']} \nLeverage: {Leverage} \nSide: {closedPnlPos['side']} \nClosedPnl: {closedPnlPos['closedPnl']} \nEntryPrice: {EntryPrice} \nExitPrice: {ExitPrice} \nPnlPercent: {-round((((EntryPrice / ExitPrice) * 100) - 100) * Leverage, 2)}% \nPositionTestNumber: {posNum}'
            send_message_to_channel(Messege)
            print(f"Сообщение отправлено в канал! \nСообщение: \n{Messege}")

        time.sleep(5)
    except Exception as er:
        print(er)