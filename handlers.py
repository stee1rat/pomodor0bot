from utils import send_message, remove_job_if_exists, get_message


def help(update, context):
    send_message(
        update,
        ("Hi, I'm your Pomodoro Timer. Let's work? Send me minutes to set "
         "the timer to or press button below. \n\nIn a group please send "
         "commands like this: /25@pomodoro_timer_bot.")
    )


def report(context):
    job = context.job.context

    if job['sprint'] and job['pomodoros'] < 4:
        set_timer(
            job['update'],
            job['context'],
            job['sprint'],
            not job['rest'],
            job['pomodoros'] + 1 if job['rest'] else job['pomodoros']
        )
        return

    if job['sprint']:
        text = "Congratulations, your sprint is done! How do you feel?"
    else:
        text = f"Pomodoro {job['due']} minutes is over! How's it going?"

    context.bot.send_message(job['chat_id'], text=text)


def set_timer(update, context, sprint=False, rest=False, pomodoros=0):
    chat_id = update.effective_message.chat_id

    if sprint:
        due = 30 if not rest else 10
    else:
        due = int(update.message['text'][1:].replace('@pomodor0bot', ''))

    job_removed = remove_job_if_exists(str(chat_id), context)

    data = {
        'pomodoros': pomodoros,
        'chat_id': chat_id,
        'context': context,
        'update': update,
        'sprint': sprint,
        'rest': rest,
        'due': due
    }

    context.job_queue.run_once(
        report, due * 60, name=str(chat_id), context=data
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
        test = "You have no active pomodoros."
    send_message(update, text)
