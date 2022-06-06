from time import time
from utils import recepient_info, send_message, get_message
from pprint import pprint

recepients = {}
statistics = {}


def alert(update, context):
    duration = update.message['text'][1:].replace('@pomodor0bot', '')
    chat_id = update.message.chat_id

    recepients[chat_id] = recepient_info(update, int(duration))

    message = f"Запущен таймер на {duration} минут"
    send_message(update, message)


def callback_minute(context):
    pprint(recepients)
    recepients_copy = recepients.copy()
    for chat_id, recepient in recepients_copy.items():
        update = recepient['update']
        duration = recepient['duration']
        start_time = recepient['start_time']
        sprint = recepient['sprint']

        minutes_since_start = (time() - start_time)/60

        if minutes_since_start > duration:
            message = get_message(sprint, duration)
            recepients.pop(chat_id)
            send_message(update, message)
            continue

        if sprint:
            if 'pomodoro_anounced' not in recepient:
                recepient['pomodoro_anounced'] = False
            if 'rest_anounced' not in recepient:
                recepient['rest_anounced'] = False

            pomodoro_duration = (time() - sprint)/60

            if pomodoro_duration >= 40 and not recepient['pomodoro_anounced']:
                recepients[chat_id]['sprint'] = time()
                message = "Pomodoro 30 minutes started."
                recepient['pomodoro_anounced'] = True
                recepient['rest_anounced'] = False
                send_message(update, message)
                continue

            if pomodoro_duration >= 30 and not recepient['rest_anounced']:
                message = "Pomodoro is done, please have 10 minutes rest now."
                recepient['rest_anounced'] = True
                recepient['pomodoro_anounced'] = False
                send_message(update, message)
                continue


def help(update, context):
    send_message(
        update,
        ("Hi, I'm your Pomodoro Timer. Let's work? Send me minutes to set "
         "the timer to or press button below. \n\nIn a group please send "
         "commands like this: /25@pomodoro_timer_bot.")
    )


def start_sprint(update, context):
    chat_id = update.message.chat_id
    duration = 150

    recepients[chat_id] = recepient_info(update, duration, time())

    message = ("Sprint started. It will last for 2 hours and 30 minutes "
               "or until you stop it. Pomodoro 30 minutes started.")

    send_message(update, message)


def stop_timer(update, context):
    chat_id = update.message.chat_id

    if chat_id in recepients:
        recepients.pop(chat_id)
        message = 'Напоминания отключены.'
    else:
        message = 'У вас не запланировано никаких напоминаний.'

    send_message(update, message)
