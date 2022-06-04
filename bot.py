import logging
import settings

from telegram.ext import CommandHandler
from telegram.ext import Updater

recepients = {}

logging.basicConfig(filename='bot.log', 
                    level=logging.INFO, 
                    format=settings.LOGGING_FORMAT)

def start_timer(update, context):
    username = update.message.from_user['username']
    recepients[username] = update
    update.message.reply_text("Напомню о себе через минуту!")

def stop_timer(update, context):
    username = update.message.from_user['username']
    if username in recepients:
        recepients.pop(username)
        update.message.reply_text('Напоминания отключены.')
    else:
        update.message.reply_text('У вас не запланировано никаких напоминаний.')

def callback_minute(context):
    print(recepients)
    for username in recepients:
        recepients[username].message.reply_text('BEEP')

def main():
    bot = Updater(settings.API_KEY, use_context=True)
    dp = bot.dispatcher
    job = bot.job_queue
    job.run_repeating(callback_minute, interval=60, first=10)
    dp.add_handler(CommandHandler('start', start_timer))
    dp.add_handler(CommandHandler('stop', stop_timer))
    bot.start_polling()
    bot.idle()

if __name__ == "__main__":
    main()