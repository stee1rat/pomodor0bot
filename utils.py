from telegram import ReplyKeyboardMarkup
from time import time


def get_message(sprint, duration):
    if sprint:
        return "Congratulations, your sprint is done! How do you feel?"
    else:
        return f"{duration} минут истекли"


def keyboard():
    return ReplyKeyboardMarkup(
        [['/5', '/15', '/25'],
         ['/start_sprint'],
         ['/help', '/stats', '/repeat', '/stop']],
        resize_keyboard=True)


def recepient_info(update, duration, sprint=False):
    return {
        "update": update,
        "duration": duration,
        "start_time": time(),
        "sprint": sprint
    }


def send_message(update, message):
    if update.message.chat_id > 0:
        update.message.reply_text(message, reply_markup=keyboard())
    else:
        update.message.reply_text(message, quote=False)
