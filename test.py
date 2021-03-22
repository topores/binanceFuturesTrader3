
from datetime import timedelta

from trader import *

from datetime import datetime

#Trader.open_position(('ETHUSDT','XRPUSDT'), pos='SHORT', test=False)
#Trader.iterate(test=True)
w=BinanceFutures.get_window('ETHUSDT')
#print(w)
print(BinanceFutures.get_server_time())

#raise Exception('end')


def set_target(now):
    target=now+timedelta(minutes=1)
    #target.minute=0
    target=target.replace(second=0, microsecond=0)
    return target


target=set_target(datetime.now())
print(target)
Trader.notify()
Trader.iterate()
while True:
    if datetime.now()>target:
        print(datetime.now(),'>',target)

        Trader.iterate()

        target = set_target(datetime.now())


