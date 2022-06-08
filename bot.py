import logging
import settings

from handlers import set_timer
from handlers import help
from handlers import repeat
from handlers import report_stats
from handlers import start_sprint
from handlers import unset_timer

from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.ext import ConversationHandler

from telegram  import ReplyKeyboardMarkup

from utils import keyboard
from utils import get_sprint_settings

CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)
POMODORO_DURATION, REST_DURATION, POMODOROS = (
    "Pomodoro duration", "Rest duration", "Number of pomodoros in a sprint")


def settings_keyboard():
    return ReplyKeyboardMarkup(
        [[POMODORO_DURATION],
         [REST_DURATION],
         [POMODOROS],
         ["Done"]], 
        one_time_keyboard=True, 
        resize_keyboard=True
    )

logging.basicConfig(filename='bot.log',
                    level=logging.INFO,
                    format=settings.LOGGING_FORMAT)


def get_settings_message(context):
    chat_settings = get_sprint_settings(context.chat_data)['settings']

    return (f"Your current settings are: \n\n"
            f"{POMODORO_DURATION}: {chat_settings[POMODORO_DURATION]}\n"
            f"{REST_DURATION}: {chat_settings[REST_DURATION]}\n"
            f"{POMODOROS}: {chat_settings[POMODOROS]}\n\n"
            f"What do you want to change?")
    

def settings_start(update, context):
    # if 'settings' not in context.chat_data:
    #     context.chat_data['settings'] = {
    #         POMODORO_DURATION: 30,
    #         REST_DURATION: 10,
    #         POMODOROS: 4
    #     }
    
    text = get_settings_message(context)

    update.message.reply_text(
        text, 
        reply_markup=settings_keyboard()
    )

    return CHOOSING


def regular_choice(update, context):
    text = update.message.text
    context.chat_data["choice"] = text
    update.message.reply_text(
        f"Please enter {text.lower()}:"
    )
    return TYPING_REPLY


def done(update, context):
    chat_data = context.chat_data
    if "choice" in chat_data:
        del chat_data["choice"]

    update.message.reply_text(
        f"Settings saved!",
        reply_markup=keyboard(), 
        quote=False
    )

    return ConversationHandler.END


def received_information(update, context):
    print("TYPING REPLY")
    chat_data = context.chat_data
    text = update.message.text
    category = chat_data["choice"]
    chat_data[category] = text

    chat_settings = context.chat_data['settings']
    chat_settings[category] = int(text)

    del chat_data["choice"]

    text = f"You entered {text} for {category.lower()}" 
    text += get_settings_message(context)
    update.message.reply_text(text, reply_markup=settings_keyboard())

    return CHOOSING


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

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("settings", settings_start)],
        states={
            CHOOSING: [
                MessageHandler(
                    Filters.regex(
                        f"^({POMODORO_DURATION}|{REST_DURATION}|{POMODOROS})$"
                    ),
                    regular_choice
                )
            ],
            TYPING_REPLY: [
                MessageHandler(
                    # А что если введут не цифру
                    Filters.text & ~(Filters.command | Filters.regex("^Done$")),
                    received_information,
                )
            ]
        },
        fallbacks=[MessageHandler(Filters.regex("^Done$"), done)],
    )

    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
