from email import message
from multiprocessing.connection import answer_challenge
from time import time
from utils import keyboard, recepient_info

recepients = {}


def alert(update, context):
    duration = update.message['text'][1:]
    username = update.message.from_user['username']

    recepients[username] = recepient_info(update, int(duration))

    message = f"Запущен таймер на {duration} минут"
    update.message.reply_text(message, reply_markup=keyboard())


def callback_minute(context):
    print(recepients)
    for username, recepient in recepients.items():
        update = recepient['update']
        duration = recepient['duration']
        start_time = recepient['start_time']

        minutes_since_start = (time() - start_time)/60

        if minutes_since_start > duration:
            message = f"{duration} минут истекли"
            recepients.pop(username)
            update.message.reply_text(message, reply_markup=keyboard())
            continue

        if duration > 25:
            message = 'BEEP'
            update.message.reply_text(message, reply_markup=keyboard())
            continue


def start_timer(update, context):
    username = update.message.from_user['username']
    recepients[username] = recepient_info(update, float('inf'))

    update.message.reply_text(
        "Напомню о себе через минуту!", reply_markup=keyboard()
    )


def stop_timer(update, context):
    username = update.message.from_user['username']

    if username in recepients:
        recepients.pop(username)
        message = 'Напоминания отключены.'
    else:
        message = 'У вас не запланировано никаких напоминаний.'

    update.message.reply_text(message, reply_markup=keyboard())
