import constants

from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from datetime import date


CHOOSING = constants.CHOOSING
TYPING_REPLY = constants.TYPING_REPLY
POMODORO_DURATION = constants.POMODORO_DURATION
REST_DURATION = constants.REST_DURATION
POMODOROS = constants.POMODOROS


def get_message(context, rest, pomodoros, sprint, job_removed, due):
    if not rest:
        text = ""
        if sprint and pomodoros == 0:
            chat_data = check_sprint_settings(context.chat_data)
            s = chat_data['settings']
            d = s[POMODORO_DURATION]
            p = s[POMODOROS]
            r = s[REST_DURATION]
            total_minutes = d * p + r * (p - 1)
            hours = total_minutes // 60
            minutes = total_minutes % 60
            text = (f"Sprint started. It will last for {hours} hours and "
                    f"{minutes} minutes or until you stop it. ")
        text += f"Pomodoro {due} minutes started."
    else:
        text = (f"Pomodoro is done, please have {due} minutes rest now..")

    if job_removed:
        text += " Previous timer was removed."

    return text


def get_settings_message(context):
    chat_settings = check_sprint_settings(context.chat_data)['settings']

    return (f"Your current settings are: \n\n"
            f"{POMODORO_DURATION}: {chat_settings[POMODORO_DURATION]}\n"
            f"{REST_DURATION}: {chat_settings[REST_DURATION]}\n"
            f"{POMODOROS}: {chat_settings[POMODOROS]}\n\n"
            f"What do you want to change?")


def keyboard():
    return ReplyKeyboardMarkup(
        [['/5', '/15', '/25'],
         ['/start_sprint'],
         ['/help', '/stats', '/repeat', '/stop']],
        resize_keyboard=True)


def send_message(update, message):
    if update.message.chat_id > 0:
        update.message.reply_text(message, reply_markup=keyboard())
    else:
        update.message.reply_text(
            message, reply_markup=ReplyKeyboardRemove(), quote=False
        )


def settings_keyboard():
    return ReplyKeyboardMarkup(
        [[POMODORO_DURATION],
         [REST_DURATION],
         [POMODOROS],
         ["Done"]],
        one_time_keyboard=True,
        resize_keyboard=True
    )


def remove_job_if_exists(name, context):
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True


def update_stats(chat_data, minutes):
    if ('stats' not in chat_data or
            chat_data['stats']['date'] < date.today()):
        chat_data['stats'] = {
            'pomodoros': 0,
            'minutes': 0,
            'date': date.today()
        }

    chat_data['stats']['pomodoros'] += 1
    chat_data['stats']['minutes'] += minutes


def check_sprint_settings(chat_data):
    if 'settings' not in chat_data:
        chat_data['settings'] = {
            POMODORO_DURATION: 30,
            REST_DURATION: 10,
            POMODOROS: 4
        }
    return chat_data
