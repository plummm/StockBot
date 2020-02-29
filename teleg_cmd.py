from telegram.ext import InlineQueryHandler
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import Bot

StatusNone = 0
StatusAddToWatchList = 1
StatusRemoveFromWatchList = 2
StatusGetPrice = 3

updater = None
dispatcher = None
userStatus = {}
gSym = {}
gChatId = []

def AddCommandHandler(str, func):
    handler = CommandHandler(str, func)
    dispatcher.add_handler(handler)

def AddInlineQueryHandler(func):
    handler = InlineQueryHandler(func)
    dispatcher.add_handler(handler)

def AddMessageHandler(func):
    handler = MessageHandler(Filters.text & (~ Filters.command), func)
    dispatcher.add_handler(handler)

def AddCallbackQueryHandler(func):
    handler = CallbackQueryHandler(func)
    dispatcher.add_handler(handler)

def sendMessages(chat_id, message):
    updater.bot.send_message(chat_id=chat_id, text=message)

def CommandAdd2WatchList(update, context):
    sendMessages(update.effective_chat.id, "tell me the stock's symbol")
    userStatus[update.effective_user.id] = StatusAddToWatchList

def CommandRemoveFromWatchList(update, context):
    sendMessages(update.effective_chat.id, "tell me the stock's symbol")
    userStatus[update.effective_user.id] = StatusRemoveFromWatchList

def CommandGetPrice(update, context):
    sendMessages(update.effective_chat.id, "tell me the stock's symbol")
    userStatus[update.effective_user.id] = StatusGetPrice

def CommandGetPriceFromWatchList(update, context):
    invokeKeyboard(update)

def CommandShowWatchlist(update, context):
    chat_id = update.effective_chat.id
    num = len(gSym[chat_id])
    message = str(num) + " stocks in total:\n"
    for each in gSym[chat_id]:
        message += gSym[chat_id][each]["name"] + "(" + each + ") : $"+str(gSym[chat_id][each]["currentPrice"]) + "\n"
    sendMessages(update.effective_chat.id, message)

def InlineSearchForStock(update, context):
    query = update.inline_query.query
    print(query)
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Caps',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)

def invokeKeyboard(update):
    keyboard = []
    row = []
    for each in gSym[update.effective_chat.id]:
        row.append(InlineKeyboardButton(each, callback_data=each))
        if len(row) == 6:
            keyboard.append(row)
            row = []
    keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Choose a stock:', reply_markup=reply_markup)