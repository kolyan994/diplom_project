import os
from bot import VKinderBot
from server import start_server
from threading import Thread

if __name__ == '__main__':
    bot = VKinderBot()
    bot_thread = Thread(target=bot.start_bot)
    server_thread = Thread(target=start_server)
    # server_thread.start()
    bot_thread.start()