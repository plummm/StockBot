import req_cmd
import local_cache
import teleg_cmd

from telegram import Bot
from telegram.ext import Updater
from telegram import InlineQueryResultArticle, InputTextMessageContent
from datetime import datetime, timedelta
from pytz import timezone

import logging
import time
import threading

class Stock_bot:
    def __init__(self, token):
        self.symCachePath = {}
        self.chatIdCachePath = "./chat_id"
        self.initTelegram(token)
        self.initLogging()
        self.initCache()
        #self.initTime()

    def initTelegram(self, token):
        teleg_cmd.updater = Updater(token=token, use_context=True)
        teleg_cmd.dispatcher = teleg_cmd.updater.dispatcher
        teleg_cmd.updater.start_polling()
        teleg_cmd.AddCommandHandler("add_to_watchlist", teleg_cmd.CommandAdd2WatchList)
        teleg_cmd.AddCommandHandler("remove_from_watchlist", teleg_cmd.CommandRemoveFromWatchList)
        teleg_cmd.AddCommandHandler("get_price", teleg_cmd.CommandGetPrice)
        teleg_cmd.AddCommandHandler("get_price_from_watchlist", teleg_cmd.CommandGetPriceFromWatchList)
        teleg_cmd.AddCommandHandler("show_the_watchlist", teleg_cmd.CommandShowWatchlist)
        teleg_cmd.AddInlineQueryHandler(teleg_cmd.InlineSearchForStock)
        teleg_cmd.AddCommandHandler("start", self.CommandStart)
        teleg_cmd.AddMessageHandler(self.MessageUnknowText)
        teleg_cmd.AddCallbackQueryHandler(self.CallbackStockPick)
        teleg_cmd.AddCommandHandler("enable_nofitication",
                                    self.CommandEnableNotification)
        teleg_cmd.AddCommandHandler("disable_nofitication_",
                                    self.CommandDisableNotification)

    def initCache(self):
        ids = self.__getLocalChatId()
        for id in ids:
            self.symCachePath[id] = "./sym-"+str(id)
            self.__getLocalSym(id)

    def initLogging(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    def initTime(self):
        nyc = timezone('America/New_York')
        today = datetime.today().astimezone(nyc)
        today_str = datetime.today().astimezone(nyc).strftime('%Y-%m-%d')
        calendar = req_cmd.getMarketCalendar(today_str)
        market_open = today.replace(
            hour=calendar.open.hour,
            minute=calendar.open.minute,
            second=0
        )
        market_open = market_open.astimezone(nyc)
        market_close = today.replace(
            hour=calendar.close.hour,
            minute=calendar.close.minute,
            second=0
        )
        market_close = market_close.astimezone(nyc)

        current_dt = datetime.today().astimezone(nyc)
        self.__prepareWatcher(market_open, market_close)

    #def watchPriceTrend(self, market_open, market_close, sym2ChatId):

    def showThePrice(self, update, sym):
        price = self.__getPrice(sym)
        if price != -1:
            teleg_cmd.sendMessages(update.effective_chat.id, "Current price of " + sym + " is $" + str(price))
            if sym in teleg_cmd.gSym[update.effective_chat.id]:
                teleg_cmd.gSym[update.effective_chat.id][sym]["currentPrice"] = price

    def Add2WatchList(self, chat_id, sym):
        print(teleg_cmd.gSym)
        if sym not in teleg_cmd.gSym[chat_id]:
            detail = req_cmd.getDetail(sym)
            if self.__validSym(detail):
                teleg_cmd.gSym[chat_id][sym] = detail
                self.__write2LocalSym(chat_id, teleg_cmd.gSym)
                return True
            else:
                return False

    def RemoveFromWatchList(self, chat_id, sym):
        res = False
        if sym in teleg_cmd.gSym[chat_id]:
            res = True
            teleg_cmd.gSym[chat_id].pop(sym)
        self.__write2LocalSym(chat_id, teleg_cmd.gSym)
        return res

    def CommandStart(self, update, context):
        chat_id = update.effective_chat.id
        self.symCachePath[chat_id] = "./sym-"+str(chat_id)
        self.__getLocalSym(chat_id)
        if chat_id not in teleg_cmd.gChatId:
            teleg_cmd.gChatId.append(chat_id)
            local_cache.writeToChatIdCache(self.chatIdCachePath, chat_id)
        teleg_cmd.sendMessages(update.effective_chat.id, "I'm ready!")

    def MessageUnknowText(self, update, context):
        chat_id = update.effective_chat.id
        if not self.__isChatRegistered(chat_id):
            return
        if teleg_cmd.userStatus[chat_id] == teleg_cmd.StatusAddToWatchList:
            if self.Add2WatchList(chat_id, update.message.text):
                teleg_cmd.sendMessages(chat_id, update.message.text + " has been added to the watchlist.\n"
                                       + "The current price is $" + str(teleg_cmd.gSym[chat_id][update.message.text]["currentPrice"]))
            else:
                teleg_cmd.sendMessages(chat_id, update.message.text + " is not a valid stock symbol.")
        elif teleg_cmd.userStatus[chat_id] == teleg_cmd.StatusRemoveFromWatchList:
            if self.RemoveFromWatchList(chat_id, update.message.text):
                teleg_cmd.sendMessages(chat_id, update.message.text + " has been removed from the watchlist.")
            else:
                teleg_cmd.sendMessages(chat_id, "There is no " + update.message.text + " in the watchlist.")
        elif teleg_cmd.userStatus[chat_id] == teleg_cmd.StatusGetPrice:
            self.showThePrice(update, update.message.text)

        teleg_cmd.userStatus[chat_id] = teleg_cmd.StatusNone

    def CallbackStockPick(self, update, context):
        query = update.callback_query
        query.edit_message_text(text="Selected stock: {}".format(query.data))
        self.showThePrice(update, query.data)

    def CommandEnableNotification(self, update, context):
        pass
        #chat_id = update.effective_chat.id
        #if chat_id not in teleg_cmd.gChatId:
        #    teleg_cmd.gChatId.append(chat_id)
        #    local_cache.writeToChatIdCache(self.chatIdCachePath, teleg_cmd.gChatId)

    def CommandDisableNotification(self, update, context):
        pass
        #chat_id = update.effective_chat.id
        #if chat_id in teleg_cmd.gChatId:
        #    teleg_cmd.gChatId.remove(chat_id)
        #    local_cache.overwriteToChatIdCache(self.chatIdCachePath, teleg_cmd.gChatId)

    def GetOpenStockInfo(self):
        t = time.time()

    def __validSym(self, detail):
        return req_cmd.getValidation(detail)

    def __getPrice(self, sym):
        return req_cmd.getPrice(sym)

    def __getLocalSym(self, chat_id):
        sym = local_cache.readFromSymsCache(self.symCachePath[chat_id])
        if str(chat_id) in sym:
            teleg_cmd.gSym[chat_id] = sym[str(chat_id)]
        else:
            teleg_cmd.gSym[chat_id] = {}

    def __getLocalChatId(self):
        ids = local_cache.readFromChatIdCache(self.chatIdCachePath)
        return ids

    def __write2LocalSym(self, chat_id, syms):
        local_cache.writeToSymsCache(self.symCachePath[chat_id], syms)

    def __isChatRegistered(self, chat_id):
        if chat_id not in teleg_cmd.gChatId:
            teleg_cmd.sendMessages(chat_id, "/start first.")
            return False
        return True

    def __prepareWatcher(self, market_open, market_close):
        sym2ChatId = {}
        for id in teleg_cmd.gSym:
            for sym in teleg_cmd.gSym[id]:
                if len(sym2ChatId[sym]) == 0:
                    sym2ChatId[sym] = []
                if id not in sym2ChatId[sym]:
                    sym2ChatId[sym].append(id)
        th = threading.Thread(target=self.watchPriceTrend(), args=(market_open, market_close, sym2ChatId))
        th.start()

