from utils import get_message
from utils import remove_job_if_exists
from utils import update_stats
from utils import send_message


def help(update, context):
    send_message(
        update,
        ("Hi, I'm your Pomodoro Timer. Let's work? Send me minutes to set "
         "the timer to or press button below. \n\nIn a group please send "
         "commands like this: /25@pomodoro_timer_bot.")
    )


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

    if job['rest'] or not job['sprint']:
        update_stats(job['context'].chat_data, job['due'])

    if job['sprint'] and job['pomodoros'] < 4:
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
        due = 30 if not rest else 10
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

    context.job_queue.run_once(
        report, due, name=str(chat_id), context=data
    )

    text = get_message(rest, pomodoros, sprint, job_removed, due)
    send_message(update, text)


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
