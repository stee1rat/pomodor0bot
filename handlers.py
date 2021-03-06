import constants

from utils import get_message
from utils import get_settings_message
from utils import remove_job_if_exists
from utils import update_stats
from utils import send_message
from utils import settings_keyboard
from utils import check_sprint_settings

from telegram.ext import ConversationHandler


CHOOSING = constants.CHOOSING
TYPING_REPLY = constants.TYPING_REPLY
POMODORO_DURATION = constants.POMODORO_DURATION
REST_DURATION = constants.REST_DURATION
POMODOROS = constants.POMODOROS


def choice(update, context):
    text = update.message.text

    context.chat_data["choice"] = text
    update.message.reply_text(f"Please enter {text.lower()}:")

    return TYPING_REPLY


def done(update, context):
    if "choice" in context.chat_data:
        del context.chat_data["choice"]

    send_message(update, "Settings saved!")

    return ConversationHandler.END


def help(update, context):
    send_message(
        update,
        ("Hi, I'm your Pomodoro Timer. Let's work? Send me minutes to set "
         "the timer to or press button below. \n\nIn a group please send "
         "commands like this: /25@pomodoro_timer_bot.")
    )


def received_information(update, context):
    try:
        text = update.message.text
        chat_data = context.chat_data
        category = chat_data["choice"]
        chat_settings = chat_data['settings']

        chat_settings[category] = int(text)

        del chat_data["choice"]

        text = f"You entered {text} for {category.lower()}"
        text += get_settings_message(context)
        update.message.reply_text(text, reply_markup=settings_keyboard())

        return CHOOSING

    except ValueError:
        send_message(update, "The answer should be a number!")


def repeat(update, context):
    if 'repeat' in context.chat_data:
        previous = context.chat_data['repeat']
        set_timer(
            previous['update'],
            previous['context'],
            previous['sprint']
        )
    else:
        send_message(update, "You have nothing to repeat")


def report(context):
    job = context.job.context
    chat_data = job['context'].chat_data
    chat_data = check_sprint_settings(chat_data)
    sprint_settings = chat_data['settings']

    if job['rest'] or not job['sprint']:
        update_stats(chat_data, job['due'])

    if job['sprint'] and job['pomodoros'] < sprint_settings[POMODOROS]:
        set_timer(
            job['update'],
            job['context'],
            job['sprint'],
            job['rest'],
            job['pomodoros']
        )
        return

    if job['sprint']:
        text = "Congratulations, your sprint is done! How do you feel?"
    else:
        text = f"Pomodoro {job['due']} minutes is over! How's it going?"

    context.bot.send_message(job['chat_id'], text=text)


def report_stats(update, context):
    if 'stats' not in context.chat_data:
        text = ("You have no completed pomodoros today. "
                "But don't be upset! There is still time to start one.")
    else:
        p = context.chat_data['stats']['pomodoros']
        m = context.chat_data['stats']['minutes']
        text = f"You did {p} pomodoros ({m} minutes) today. Good job!"
    send_message(update, text)


def set_timer(update, context, sprint=False, rest=False, pomodoros=0):
    chat_id = update.effective_message.chat_id

    if sprint:
        chat_data = check_sprint_settings(context.chat_data)
        sprint_settings = chat_data['settings']
        if not rest:
            due = sprint_settings[POMODORO_DURATION]
        else:
            due = sprint_settings[REST_DURATION]
    else:
        due = int(update.message['text'][1:].replace('@pomodor0bot', ''))

    job_removed = remove_job_if_exists(str(chat_id), context)

    data = {
        'pomodoros': pomodoros + 1 if not rest else pomodoros,
        'chat_id': chat_id,
        'context': context,
        'update': update,
        'sprint': sprint,
        'rest': not rest,
        'due': due
    }

    if pomodoros == 0:
        context.chat_data['repeat'] = data

    context.job_queue.run_once(report, due, name=str(chat_id), context=data)

    text = get_message(context, rest, pomodoros, sprint, job_removed, due)
    send_message(update, text)


def settings_start(update, context):
    text = get_settings_message(context)
    update.message.reply_text(text, reply_markup=settings_keyboard())
    return CHOOSING


def start_sprint(update, context):
    set_timer(update, context, sprint=True)


def unset_timer(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    if job_removed:
        text = "Pomodoro successfully cancelled!"
    else:
        text = "You have no active pomodoros."
    send_message(update, text)
