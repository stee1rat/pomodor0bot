from telegram import ReplyKeyboardMarkup

def keyboard():
    return ReplyKeyboardMarkup([['/5', '/15', '/25'],
                                ['/start_sprint'],
                                ['/help', '/stats', '/repeat', '/stop']],
                               resize_keyboard=True)