import constants
import logging
import settings

from handlers import done
from handlers import help
from handlers import received_information
from handlers import repeat
from handlers import report_stats
from handlers import choice
from handlers import set_timer
from handlers import settings_start
from handlers import start_sprint
from handlers import unset_timer

from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext import ConversationHandler


logging.basicConfig(filename='bot.log',
                    level=logging.INFO,
                    format=settings.LOGGING_FORMAT)


def main():
    updater = Updater(settings.API_KEY, use_context=True)

    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('stats', report_stats))
    updater.dispatcher.add_handler(CommandHandler('stop', unset_timer))
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

    updater.dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("settings", settings_start)],
            states={
                constants.CHOOSING: [
                    MessageHandler(
                        Filters.regex((
                            f"^({constants.POMODORO_DURATION}|"
                            f"{constants.REST_DURATION}|"
                            f"{constants.POMODOROS})$"
                        )),
                        choice
                    )
                ],
                constants.TYPING_REPLY: [
                    MessageHandler(
                        Filters.text & ~(Filters.command |
                                         Filters.regex("^Done$")),
                        received_information,
                    )
                ]
            },
            fallbacks=[MessageHandler(Filters.regex("^Done$"), done)],
        )
    )

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
