import pandas as pd
import pickle
import datetime

ticker_list = ['ETHUSDT', 'LTCUSDT', 'ETCUSDT', 'XRPUSDT']
pair_list = [('ETHUSDT', 'LTCUSDT'), ('ETHUSDT', 'ETCUSDT'), ('ETHUSDT', 'XRPUSDT'), ('LTCUSDT', 'ETCUSDT'),
             ('LTCUSDT', 'XRPUSDT'), ('ETCUSDT', 'XRPUSDT')]
min_pip_list = {
    'ETHUSDT': 3,
    'LTCUSDT': 3,
    'ETCUSDT': 2,
    'XRPUSDT': 0

}


class Storage():
    def __init__(self):
        self.payload = {}

        self.payload['tickers_info'] = dict(zip(ticker_list, [[None]] * 4))
        self.payload['server_time'] = 0
        self.payload['balance'] = 0
        # self.dump()

    def update(self, BinanceFutures):
        ticker_dict = {}

        for ticker in ticker_list:
            ticker_dict[ticker] = BinanceFutures.get_window(ticker)
            if type(ticker_dict[ticker]) == type(None):
                raise Exception('fail to get ' + ticker + ' data')
        self.payload['tickers_info'] = ticker_dict
        self.payload['server_time'] = BinanceFutures.get_server_time()
        self.payload['balance'] = float(BinanceFutures.get_account_info()['totalMarginBalance'])

    def get(self):
        return self.payload

    def get_balance(self):
        return self.payload['balance']

    def get_df(self, ticker):
        return self.payload['tickers_info'][ticker]

    def get_pair_dfs(self, pair):
        return self.get_df(pair[0]), self.get_df(pair[1])

    def dump(self, filename="storage.pickle"):
        pickle.dump(self.payload, open(filename, 'wb'))

    def load(self, filename="storage.pickle"):
        self.payload = pickle.load(open(filename, 'rb'))


class Positions(object):
    def __init__(self):

        self.payload = {
            'quantities': dict(zip(pair_list, [None] * len(pair_list))),
            'closes': dict(zip(pair_list, [None] * len(pair_list)))
        }

    def load(self, filename='positions.pickle'):
        self.payload = pickle.load(open(filename, 'rb'))

    def dump(self, filename='positions.pickle'):
        pickle.dump(self.payload, open(filename, 'wb'))

    def close(self, pair):
        self.payload['quantities'][pair] = None
        self.payload['closes'][pair] = None

    def open(self, pair, quantities,closes=(1,-1)):
        self.payload['quantities'][pair] = quantities
        self.payload['closes'][pair] = closes

    def get_quantities(self):
        return self.payload['quantities']

    def get_closes(self):
        return self.payload['closes']

    def get_pair_quantities(self, pair):
        return self.payload['quantities'][pair]

    def get_pair_closes(self, pair):
        return self.payload['closes'][pair]

    def get_pair_spread(self,pair):
        a=self.payload['closes'][pair]
        return a[0]/a[1]

    def get_pair_side(self, pair):
        if self.payload['quantities'][pair][0] > 0:
            return "LONG"
        else:
            return "SHORT"

    def get_pair_info(self, pair):
        return self.payload_info[pair]

    def set_pair_info(self, pair):  # !!!!!
        pass
