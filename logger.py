
import telebot
from telebot.types import InputMediaPhoto
import matplotlib.pyplot as plt
#inputFile
token = 'token'
bot = telebot.TeleBot(token)
CHANNEL_NAME = 'channel_name'

def log(message):
    send_telegram_message(message)
    print("***NEW LOG:***")
    print(message)
    print()
def log_w_picture(message,pic):
    send_telegram_photo_message(pic,message)
    print("***NEW LOG:***")
    print(message)
    print()

def send_telegram_message(S):
    S+="\n(c) binanceFuturesTrader"
    try:
        bot.send_message(CHANNEL_NAME, S)
        #print("\niTelegrammer sended :\n", S,"\n")

    except Exception as e:
        print("\niTelegrammer try to send :\n", S, "\n")
        print("but: Telegram doesn't available now:\n", e,"\n")
def send_telegram_photo_message(photo,S):
    try:
        bot.send_photo(CHANNEL_NAME, photo,caption=S)
        #print("\niTelegrammer sended :\n", S,"\n")
    except Exception as e:
        print("but: Telegram doesn't available now:\n", e,"\n")

def gen_photo(data):
    plt.clf()
    for series in data:
        plt.plot(series)
    plt.savefig('chart.png')
    return open('chart.png', 'rb')

#plt.plot([1,2,3,4,3,2,3,4,5,3,6,5,4,5,6,7,10,8,7,6,7,8,9])
#plt.savefig('test.png')