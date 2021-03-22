from algorithm import *
from binance_futures import *
from storage import *
import logger
from collections import deque


class Event():
    def __init__(self, event_type, pair, side=None):
        self.event_type = event_type
        self.pair = pair
        self.side = side
        self.quantities = None

    def set_test_mode(self,mode):
        self.test_mode = mode
    def set_quantities(self, quantities, mode="OPEN"):
        if mode == "OPEN":
            self.quantities = quantities
        elif mode == "CLOSE":
            self.quantities = (-quantities[0], -quantities[1])
            print('closing position: quantities reversed')
        else:
            raise Exception('incorrect mode (OPEN?CLOSE)')

    def execute(self):



        position = Position(self.pair[0], self.quantities[0])
        BinanceFutures.send_order(position, safe=True)

        position = Position(self.pair[1], self.quantities[1])
        BinanceFutures.send_order(position, safe=True)
        logger.log('Successfully executed...\n' + str(self))

    def __str__(self):
        s='Event object:\n---------------\n'
        for key in self.__dict__:
            s+='\t'+str(key)+': '+str(self.__dict__[key])+'\n'
        '---------------'
        return s



class Trader(object):
    storage = Storage()
    positions = Positions()
    leverage=22
    base_stake = 0.2*leverage
    test_mode=False
    @staticmethod
    def check_for_close(pair, side):
        (t1, t2) = pair
        df1, df2 = Trader.storage.get_df(t1), Trader.storage.get_df(t2)
        return Algorithm.analyse_pair_close(df1, df2, t1, t2, side,open_spread=Trader.positions.get_pair_spread(pair))

    @staticmethod
    def check_for_open(pair):
        (t1, t2) = pair
        df1, df2 = Trader.storage.get_df(t1), Trader.storage.get_df(t2)
        return Algorithm.analyse_pair_open(df1, df2, t1, t2)

    @staticmethod
    def execute(event):
        #BINANCE
        if event.event_type == "CLOSE":
            event.set_quantities(Trader.positions.get_pair_quantities(event.pair), mode="CLOSE")
        elif event.event_type == "OPEN":

            df1, df2 = Trader.storage.get_pair_dfs(event.pair)

            kvar1, kvar2 = Algorithm.get_k(df1, event.pair[0]), Algorithm.get_k(df2, event.pair[1])
            k1, k2 = kvar2 / (kvar1 + kvar2), kvar1 / (kvar1 + kvar2)

            p1, p2 = Algorithm.get_price(df1, event.pair[0]), Algorithm.get_price(df2, event.pair[1])

            q1 = round(k1 * (Trader.storage.get_balance()*Trader.base_stake)/ p1, Position.min_pip_list[event.pair[0]])
            q2 = round(k2 * (Trader.storage.get_balance()*Trader.base_stake) / p2, Position.min_pip_list[event.pair[1]])

            if event.side == "LONG":
                qs = (q1, -q2)
            elif event.side == "SHORT":
                qs = (-q1, q2)
            else:
                raise Exception('incorrect event side')
            event.set_quantities(qs, mode="OPEN")
        else:
            raise Exception('incorrect event type')

        #EXCECUTION
        if not Trader.test_mode:
            event.execute()
        else:
            logger.log('Virtually executed: '+str(event))
        #END OF EXCECUTION


        #DBS
        if event.event_type == "CLOSE":
            Trader.positions.close(event.pair)
        elif event.event_type == "OPEN":
            df1, df2 = Trader.storage.get_pair_dfs(event.pair)
            p1, p2 = Algorithm.get_price(df1, event.pair[0]), Algorithm.get_price(df2, event.pair[1])
            Trader.positions.open(event.pair, event.quantities, closes=(p1,p2))
        else:
            raise Exception('incorrect event type')


    @staticmethod
    def iterate():
        events_exist_flag = False

        Trader.storage.update(BinanceFutures)
        Trader.positions.load()
        to_open,to_close = Algorithm.divide_pairs(Trader.positions.get_quantities())
        event_queue = deque()

        for pair in to_close:
            side = Trader.positions.get_pair_side(pair)
            if Trader.check_for_close(pair, side) == "CLOSE":
                event = Event("CLOSE", pair)
                event_queue.append(event)

        for pair in to_open:
            side = Trader.check_for_open(pair)
            if side != "HOLD":
                event = Event("OPEN", pair, side=side)
                event_queue.append(event)

        if event_queue:
            logger.log('Some events are going to be executed:'+str(len(event_queue)))
            events_exist_flag=True
        while event_queue:
            event = event_queue.popleft()
            Trader.execute(event)

        del event_queue

        Trader.positions.dump()
        logger.log('Iteration done')

        if events_exist_flag:
            info=BinanceFutures.get_account_info()
            logger.log('Account wallet balance: '+str(info['totalWalletBalance']+'\nAccount margin balance: '+str(info['totalMarginBalance'])))

        del to_close
        del to_open

    @staticmethod
    def set_leverage(leverage):
        mess=''
        for ticker in ticker_list:
            if (BinanceFutures.set_leverage(ticker, leverage)):
                print(ticker, '- leverages setted')
            else:
                print(ticker, '- leverages setting fail')
                mess+=ticker + '- leverages setting fail\n'
            mess+='Leverages is ' + str(leverage) + ' now'+'\n'
        logger.log(mess)

    @staticmethod
    def notify(msg=None):
        if msg == None:
            logger.log('BOT STARTED!')
        else:
            logger.log(str(msg))
