from binance_f import RequestClient
from binance_f.constant.test import *
from binance_f.base.printobject import *
from binance_f.model.constant import *
import logger
from config import *
import time
import pandas as pd


class Position(object):
    min_pip_list = {
        'ETHUSDT': 3,
        'LTCUSDT': 3,
        'ETCUSDT': 2,
        'XRPUSDT': 0

    }

    def __init__(self, ticker, quantity, side=None):
        if side != None:
            self.ticker = ticker
            self.side = side
            self.quantity = ('{:.' + str(Position.min_pip_list[ticker]) + 'f}').format(quantity)
        else:
            self.ticker = ticker
            if quantity >= 0:
                self.side = OrderSide.BUY
                self.quantity = ('{:.' + str(Position.min_pip_list[ticker]) + 'f}').format(quantity)
            else:
                # example: -2.3 == Sell 2.3
                self.side = OrderSide.SELL
                self.quantity = ('{:.' + str(Position.min_pip_list[ticker]) + 'f}').format(-quantity)

    def __str__(self):
        return 'symbol: ' + str(self.ticker) + '\nside: ' + str(self.side) + '\nquantity: ' + str(self.quantity)


class BinanceFutures(object):
    current_exception = None

    @staticmethod
    def send_order(position, safe=False):
        if not safe:
            try:
                print('trying to send Order:\n', position)
                request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)
                result = request_client.post_order(symbol=position.ticker, side=position.side,
                                                   ordertype=OrderType.MARKET,
                                                   quantity=position.quantity)
                # PrintBasic.print_obj(result)
                return True

            except Exception as e:
                print(e)
                BinanceFutures.current_exception = e
                time.sleep(1)
                return False
        else:
            sleep_time = 1
            while True:
                result = BinanceFutures.send_order(position, safe=False)
                if result:
                    break
                else:
                    logger.log('Exception in safe_open_order execution:\n' + str(
                        BinanceFutures.current_exception) + '\n\nSleeping for' + str(sleep_time) + 'seconds')

                    time.sleep(sleep_time)
                    sleep_time *= 2

    @staticmethod
    def get_position():
        try:
            request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)
            result = request_client.get_position()
            # PrintBasic.print_obj(result)
            return result

        except Exception as e:
            print(e)
            time.sleep(1)
            return None

    @staticmethod
    def get_server_time():

        try:
            request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)
            result = request_client.get_servertime()
            return result["serverTime"]

        except Exception as e:
            print(e)
            time.sleep(1)
            return None

    @staticmethod
    def get_window(symbol):
        print('getting', symbol, 'dataframe')

        try:
            request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)

            result = request_client.get_candlestick_data(symbol=symbol, interval=CandlestickInterval.MIN15,
                                                         startTime=None, endTime=None, limit=400)
            df = pd.DataFrame(data=result,
                              columns=['time', 'O', 'H', 'L', 'C', 'vol', 'close_time', 'qa_volume',
                                       'nb_trades', 'tba_valume', 'tqa_valume', 'ignore'])
            # print(df[['time','close_time','O',"C"]])
            df[symbol] = df['O'].astype(float)
            df['time'] = df['time'].astype(int)
            df = df[['time', symbol]]

            return df

        except Exception as e:
            print(e)
            time.sleep(1)
            return None

    @staticmethod
    def set_leverage(symbol, leverage):
        try:
            request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)
            result = request_client.change_initial_leverage(symbol=symbol, leverage=leverage)
            return True

        except Exception as e:
            print(e)
            time.sleep(1)
            return False

    @staticmethod
    def get_account_info():
        try:
            request_client = RequestClient(api_key=g_api_key, secret_key=g_secret_key)
            result = request_client.get_account_information()
            return result

        except Exception as e:
            print(e)
            time.sleep(1)
            return None

# print(g_api_key, g_secret_key)
#BinanceFutures.get_window("ETHUSDT")
print(BinanceFutures.get_account_info())
