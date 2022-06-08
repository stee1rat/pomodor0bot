from telegram import ReplyKeyboardMarkup
from datetime import date


POMODORO_DURATION, REST_DURATION, POMODOROS = (
    "Pomodoro duration", "Rest duration", "Number of pomodoros in a sprint")


def get_message(context, rest, pomodoros, sprint, job_removed, due):
    if not rest:
        text = ""
        if sprint and pomodoros == 0:
            chat_data = get_sprint_settings(context.chat_data)
            s = chat_data['settings']
            total_minutes = s[POMODORO_DURATION]*s[POMODOROS]
            total_minutes += s[REST_DURATION]*(s[POMODOROS] - 1)
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
        update.message.reply_text(message, quote=False)


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


def get_sprint_settings(chat_data):
    if 'settings' not in chat_data:
        chat_data['settings'] = {
            POMODORO_DURATION: 30,
            REST_DURATION: 10,
            POMODOROS: 4
        }
    return chat_data