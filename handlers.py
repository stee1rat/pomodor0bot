from time import time
from utils import keyboard

recepients = {}

def alert(update, context):
    duration = int(update.message['text'][1:])
    username = update.message.from_user['username']

    recepients[username] = { 
        "update": update, "duration": duration, "start_time": time()
    }

    update.message.reply_text(
        f"Запущен таймер на {duration} минут", reply_markup=keyboard()
    )

def callback_minute(context):
    print(recepients)
    for recepient in recepients:
        update = recepients[recepient]['update']
        duration = recepients[recepient]['duration']
        start_time = recepients[recepient]['start_time']

        if (time() - start_time)/60 > duration:
            update.message.reply_text(
                f"{duration} минут истекли", reply_markup=keyboard())
            recepients.pop(recepient)

        if duration > 25:
            update.message.reply_text('BEEP', reply_markup=keyboard())

def start_timer(update, context):
    username = update.message.from_user['username']

    recepients[username] = { 
        "update": update, "duration": float('inf'), "start_time": time() 
    }

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