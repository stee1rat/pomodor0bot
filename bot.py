import logging
import settings

from handlers import callback_minute, start_timer, stop_timer, alert
from telegram.ext import CommandHandler
from telegram.ext import Updater

logging.basicConfig(filename='bot.log',
                    level=logging.INFO,
                    format=settings.LOGGING_FORMAT)


def main():
    updater = Updater(settings.API_KEY, use_context=True)

    job = updater.dispatcher.job_queue
    job.run_repeating(callback_minute, interval=60, first=10)

    updater.dispatcher.add_handler(CommandHandler('start', start_timer))
    updater.dispatcher.add_handler(CommandHandler('stop', stop_timer))
    updater.dispatcher.add_handler(CommandHandler('5', alert))
    updater.dispatcher.add_handler(CommandHandler('15', alert))
    updater.dispatcher.add_handler(CommandHandler('25', alert))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
