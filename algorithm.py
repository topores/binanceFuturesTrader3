import pandas as pd
import logger


class Algorithm(object):
    m = 3
    m_out = 2.5
    window_size = 80 * 4

    @staticmethod
    def divide_pairs(payload):
        to_open, to_close = [], []
        for pair in payload:
            if payload[pair] is None:
                to_open.append(pair)
            else:
                to_close.append(pair)
        return to_open, to_close

    @staticmethod
    def get_k(df, t):
        return df[t].std() / df[t].mean()

    @staticmethod
    def get_price(df, t):
        return df[t][len(df) - 1]

    @staticmethod
    def analyse_pair_open(df1, df2, t1, t2):

        df = pd.merge(df1, df2, on='time', how='inner')
        df = df.sort_values(by='time', axis=0).reset_index().drop('index', axis=1)
        df['spread'] = df[t1] / df[t2]

        df = df[len(df) - Algorithm.window_size:len(df)]
        df = df.reset_index().drop('index', axis=1)

        last = df['spread'][len(df) - 1]
        first = df['spread'][0]

        std = df['spread'].std()
        mean = df['spread'].mean()

        z = (last - mean) / std
        print(t1, t2, '| z:', z)
        if z < -Algorithm.m:
            logger.log_w_picture("OPEN found for " + t1 + "/" + t2 + " ...\nz:" + str(z) + "\nside: LONG",
                                 logger.gen_photo([df['spread'],
                                                   0 * df['spread'] + mean - Algorithm.m * std,
                                                   0 * df['spread'] + mean + Algorithm.m * std,
                                                   0 * df['spread'] + mean - Algorithm.m_out * std,
                                                   0 * df['spread'] + mean + Algorithm.m_out * std,
                                                   df[t1] / df[t1][0] * first, df[t2] / df[t2][0] * first]))

            return "LONG"

        elif z > Algorithm.m:
            logger.log_w_picture("OPEN found for " + t1 + "/" + t2 + " ...\nz:" + str(z) + "\nside: SHORT",
                       logger.gen_photo([df['spread'],
                                         0 * df['spread'] + mean - Algorithm.m * std,
                                         0 * df['spread'] + mean + Algorithm.m * std,
                                         0 * df['spread'] + mean - Algorithm.m_out * std,
                                         0 * df['spread'] + mean + Algorithm.m_out * std,
                                         df[t1] / df[t1][0] * first, df[t2] / df[t2][0] * first]))

            return "SHORT"
        else:
            '''logger.log_w_picture("hold test",
                                 logger.gen_photo([df['spread'],
                                                   0 * df['spread'] + mean - Algorithm.m * std,
                                                   0 * df['spread'] + mean + Algorithm.m * std,
                                                   0 * df['spread'] + mean - Algorithm.m_out * std,
                                                   0 * df['spread'] + mean + Algorithm.m_out * std,
                                                   df[t1] / df[t1][0] * first, df[t2] / df[t2][0] * first]))
                                                   '''
            return "HOLD"

    @staticmethod
    def analyse_pair_close(df1, df2, t1, t2, side,open_spread=-1):
        print('analysing:', t1, '/', t2, ' for close')

        df = pd.merge(df1, df2, on='time', how='inner')
        df = df.sort_values(by='time', axis=0).reset_index().drop('index', axis=1)
        df['spread'] = df[t1] / df[t2]

        df = df[len(df) - Algorithm.window_size:len(df)]
        df = df.reset_index().drop('index', axis=1)

        last = df['spread'][len(df) - 1]
        first = df['spread'][0]

        std = df['spread'].std()
        mean = df['spread'].mean()

        z = (last - mean) / std
        print(t1, t2, ":", z, ', pos =', side)

        if side == "LONG" and ((z >= -Algorithm.m_out) or (last<open_spread*0.972 and open_spread!=-1)):
            logger.log_w_picture("CLOSE found for " + t1 + "/" + t2 + " ...\nz:" + str(z),
                                 logger.gen_photo([df['spread'],
                                                    0 * df['spread'] + mean - Algorithm.m * std,
                                                    0 * df['spread']+ mean + Algorithm.m * std,
                                                    0 * df['spread']+ mean - Algorithm.m_out * std,
                                                    0 * df['spread']+ mean + Algorithm.m_out * std,
                                                  df[t1]/df[t1][0]*first, df[t2]/df[t2][0]*first]))
            return "CLOSE"
        elif side == "SHORT" and ((z <= Algorithm.m_out)  or (last>open_spread*1.029 and open_spread!=-1)):
            logger.log_w_picture("CLOSE found for " + t1 + "/" + t2 + " ...\nz:" + str(z),
                                 logger.gen_photo([df['spread'],
                                                    0 * df['spread'] + mean - Algorithm.m * std,
                                                    0 * df['spread']+ mean + Algorithm.m * std,
                                                    0 * df['spread']+ mean - Algorithm.m_out * std,
                                                    0 * df['spread']+ mean + Algorithm.m_out * std,
                                                  df[t1]/df[t1][0]*first, df[t2]/df[t2][0]*first]))
            return "CLOSE"
        else:
            return "HOLD"
