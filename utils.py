from telegram import ReplyKeyboardMarkup
from time import time


def keyboard():
    return ReplyKeyboardMarkup(
        [['/5', '/15', '/25'],
         ['/start_sprint'],
         ['/help', '/stats', '/repeat', '/stop']],
        resize_keyboard=True)


def recepient_info(update, duration):
    return {
        "update": update,
        "duration": int(duration),
        "start_time": time()
    }
