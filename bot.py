import logging
import settings

from handlers import set_timer
from handlers import help
from handlers import repeat
from handlers import start_sprint
from handlers import unset_timer

from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater


logging.basicConfig(filename='bot.log',
                    level=logging.INFO,
                    format=settings.LOGGING_FORMAT)


def main():
    updater = Updater(settings.API_KEY, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('stop', unset_timer))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('repeat', repeat))

    updater.dispatcher.add_handler(
        CommandHandler('start_sprint', start_sprint)
    )

    updater.dispatcher.add_handler(
        MessageHandler(
            Filters.regex(fr"^/(\d+)(@{updater.bot.username}){{0,1}}$"),
            set_timer
        )
    )

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
