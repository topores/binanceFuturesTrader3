
from datetime import timedelta
from trader import *
from datetime import datetime
#DB_Provider.gen_json()
#raise Exception('end')


def set_target(now):
    target=now+timedelta(minutes=15)
    target=target.replace(minute=(target.minute//15)*15,second=5, microsecond=0)
    return target


target=set_target(datetime.now())
print('targe:',target)

Trader.notify()
Trader.iterate()
Trader.set_leverage(39)
while True:
    if datetime.now()>target:
        print(datetime.now(),'>',target)
        try:
            Trader.iterate()
        except Exception as e:
            Trader.notify(msg="Exception:\n" + str(e))

        target = set_target(datetime.now())


