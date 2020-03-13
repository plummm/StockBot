import req_cmd
import local_cache
import teleg_cmd
import alpaca

from telegram import Bot
from telegram.ext import Updater
from telegram import InlineQueryResultArticle, InputTextMessageContent
from datetime import datetime, timedelta
from pytz import timezone

import logging
import time
import threading

posChange5Percent = 0
posChange10Percent = 1
posChange15Percent = 2
posChange20Percent = 3
posChange25Percent = 4
posChange30Percent = 5
posChange35Percent = 6
posChange40Percent = 7
posChange45Percent = 8
posChange50Percent = 9


class Stock_bot:
    def __init__(self, token, alpaca_api_key, alpaca_secrete_key):
        self.symCachePath = {}
        self.dailyReport = {}
        self.today = datetime.today()
        self.chatIdCachePath = "./chat_id"
        self.initTelegram(token)
        self.initAlpaca(alpaca_api_key, alpaca_secrete_key)
        self.initLogging()
        self.initCache()
        self.initTime()

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
    def initAlpaca(self, alpaca_api_key, alpaca_secrete_key):
        alpaca.setAlpacaApi(alpaca_api_key, alpaca_secrete_key)

    def initCache(self):
        ids = self.__getLocalChatId()
        for id in ids:
            if id not in teleg_cmd.gChatId:
                teleg_cmd.gChatId.append(id)
            self.symCachePath[id] = "./sym-"+str(id)
            self.__getLocalSym(id)
            for sym in teleg_cmd.gSym[id]:
                if id not in self.dailyReport:
                    self.dailyReport[id] = {}
                self.dailyReport[id][sym] = 0

    def initLogging(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)

    def initTime(self):
        nyc = timezone('America/New_York')
        self.today = datetime.today().astimezone(nyc)
        self.today -= timedelta(days=1)
        self.today = self.today.replace(
            hour=0,
            minute=0,
            second=0
        )
        th = threading.Thread(target=self.__dailyTimer)
        th.start()

    def watchPriceTrend(self, current_dt, market_open, market_close, sym2ChatId):
        before_market_open = market_open - current_dt
        since_market_open = current_dt - market_open
        print("Serval hours before market open.")
        while before_market_open.days >= 0 and before_market_open.seconds // 60 >= 60:
            time.sleep(60*60)
            before_market_open = market_open - current_dt
        print("Serval minutes before market open.")
        while before_market_open.days >= 0 and before_market_open.seconds // 60 <= 60:
            time.sleep(1)
            before_market_open = market_open - current_dt
        print("Market Opened")
        if since_market_open.seconds // 60 <= 7:
            for sym in sym2ChatId:
                price = alpaca.getMarketOpenPrice(sym)
                for chat_id in sym2ChatId[sym]:
                    self.__updatePrice(chat_id, sym, price)
            for chat_id in teleg_cmd.gChatId:
                teleg_cmd.sendMessages(chat_id, "Market Opened!")
                teleg_cmd.mergeStocksPrint(chat_id, "Market Opened Price:\n")

        before_market_close = market_close - current_dt
        while before_market_close.days >=0:
            time.sleep(300)
            for sym in sym2ChatId:
                [change, price] = alpaca.getDailyChange(sym)
                for chat_id in sym2ChatId[sym]:
                    if abs(change) > 40 and (self.dailyReport[chat_id][sym] ^ (1 << posChange40Percent)):
                        message = 'Breaking: {} moved {}% over the last one day, current price is ${}(草，不可能发生)'.format(sym, change, price)
                        teleg_cmd.sendMessages(chat_id, message)
                        self.dailyReport[chat_id][sym] ^= (1 << posChange40Percent)
                    elif abs(change) > 35 and (self.dailyReport[chat_id][sym] ^ (1 << posChange35Percent)):
                        message = 'Breaking: {} moved {}% over the last one day, current price is ${}(肯定是出bug了)'.format(sym, change, price)
                        teleg_cmd.sendMessages(chat_id, message)
                        self.dailyReport[chat_id][sym] ^= (1 << posChange35Percent)
                    elif abs(change) > 30 and (self.dailyReport[chat_id][sym] ^ (1 << posChange30Percent)):
                        message = 'Breaking: {} moved {}% over the last one day, current price is ${}'.format(sym, change, price)
                        teleg_cmd.sendMessages(chat_id, message)
                        self.dailyReport[chat_id][sym] ^= (1 << posChange30Percent)
                    elif abs(change) > 25 and (self.dailyReport[chat_id][sym] ^ (1 << posChange25Percent)):
                        message = 'Breaking: {} moved {}% over the last one day, current price is ${}'.format(sym, change, price)
                        teleg_cmd.sendMessages(chat_id, message)
                        self.dailyReport[chat_id][sym] ^= (1 << posChange25Percent)
                    elif abs(change) > 20 and (self.dailyReport[chat_id][sym] ^ (1 << posChange20Percent)):
                        message = 'Breaking: {} moved {}% over the last one day, current price is ${}'.format(sym, change, price)
                        teleg_cmd.sendMessages(chat_id, message)
                        self.dailyReport[chat_id][sym] ^= (1 << posChange20Percent)
                    elif abs(change) > 15 and (self.dailyReport[chat_id][sym] ^ (1 << posChange15Percent)):
                        message = 'Breaking: {} moved {}% over the last one day, current price is ${}'.format(sym, change, price)
                        teleg_cmd.sendMessages(chat_id, message)
                        self.dailyReport[chat_id][sym] ^= (1 << posChange15Percent)
                    elif abs(change) > 10 and (self.dailyReport[chat_id][sym] ^ (1 << posChange10Percent)):
                        message = 'Breaking: {} moved {}% over the last one day, current price is ${}'.format(sym, change, price)
                        teleg_cmd.sendMessages(chat_id, message)
                        self.dailyReport[chat_id][sym] ^= (1 << posChange10Percent)
                    elif abs(change) > 5 and (self.dailyReport[chat_id][sym] ^ (1 << posChange5Percent)):
                        message = 'Breaking: {} moved {}% over the last one day, current price is ${}'.format(sym, change, price)
                        teleg_cmd.sendMessages(chat_id, message)
                        self.dailyReport[chat_id][sym] ^= (1 << posChange5Percent)
            before_market_close = market_close - current_dt

        print("Market Closed")
        since_market_close = current_dt - market_close
        if since_market_close.seconds // 60 <= 7:
            for sym in sym2ChatId:
                price = alpaca.getCurrentPrice(sym)
                for chat_id in sym2ChatId[sym]:
                    self.__updatePrice(chat_id, sym, price)
            for chat_id in teleg_cmd.gChatId:
                teleg_cmd.sendMessages(chat_id, "Market Closed!")
                teleg_cmd.mergeStocksPrint(chat_id, "Market Closeed Price:\n")



    def showThePrice(self, update, sym):
        price = self.__getPrice(sym)
        if price != -1:
            teleg_cmd.sendMessages(update.effective_chat.id, "Current price of " + sym + " is $" + str(price))
            self.__updatePrice(update.effective_chat.id, sym, price)

    def Add2WatchList(self, chat_id, sym):
        print(teleg_cmd.gSym)
        if sym not in teleg_cmd.gSym[chat_id]:
            if sym not in self.dailyReport:
                self.dailyReport[sym] = {}
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
        print(chat_id)
        self.symCachePath[chat_id] = "./sym-"+str(chat_id)
        self.__getLocalSym(chat_id)
        if chat_id not in teleg_cmd.gChatId:
            teleg_cmd.gChatId.append(chat_id)
            local_cache.writeToChatIdCache(self.chatIdCachePath, chat_id)
        teleg_cmd.sendMessages(update.effective_chat.id, "I'm ready!")

    def MessageUnknowText(self, update, context):
        chat_id = update.effective_chat.id
        if update.effective_user == None:
            return
        user_id = update.effective_user.id
        if user_id not in teleg_cmd.userStatus:
            teleg_cmd.sendMessages(chat_id, "You shouldn't reply other's query", reply_to_message_id=chat_id)
            return
        if not self.__isChatRegistered(chat_id):
            return
        if teleg_cmd.userStatus[user_id] == teleg_cmd.StatusAddToWatchList:
            if self.Add2WatchList(chat_id, update.message.text):
                teleg_cmd.sendMessages(chat_id, update.message.text + " has been added to the watchlist.\n"
                                       + "The current price is $" + str(teleg_cmd.gSym[chat_id][update.message.text]["currentPrice"]))
            else:
                teleg_cmd.sendMessages(chat_id, update.message.text + " is not a valid stock symbol.")
        elif teleg_cmd.userStatus[user_id] == teleg_cmd.StatusRemoveFromWatchList:
            if self.RemoveFromWatchList(chat_id, update.message.text):
                teleg_cmd.sendMessages(chat_id, update.message.text + " has been removed from the watchlist.")
            else:
                teleg_cmd.sendMessages(chat_id, "There is no " + update.message.text + " in the watchlist.")
        elif teleg_cmd.userStatus[user_id] == teleg_cmd.StatusGetPrice:
            self.showThePrice(update, update.message.text)

        teleg_cmd.userStatus[user_id] = teleg_cmd.StatusNone

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
        local_cache.writeToSymsCache(self.symCachePath[chat_id], {chat_id:syms[chat_id]})

    def __isChatRegistered(self, chat_id):
        if chat_id not in teleg_cmd.gChatId:
            teleg_cmd.sendMessages(chat_id, "/start first.")
            return False
        return True

    def __updatePrice(self, chat_id, sym, price):
        if sym in teleg_cmd.gSym[chat_id]:
            teleg_cmd.gSym[chat_id][sym]["currentPrice"] = price

    def __prepareWatcher(self, current_dt, market_open, market_close):
        sym2ChatId = {}
        for id in teleg_cmd.gSym:
            for sym in teleg_cmd.gSym[id]:
                if sym not in sym2ChatId:
                    sym2ChatId[sym] = []
                if id not in sym2ChatId[sym]:
                    sym2ChatId[sym].append(id)
        th = threading.Thread(target=self.watchPriceTrend, args=(current_dt, market_open, market_close, sym2ChatId))
        th.start()

    def __dailyTimer(self):
        nyc = timezone('America/New_York')
        while True:
            today = datetime.today().astimezone(nyc)
            today = today.replace(
                hour=0,
                minute=0,
                second=0
            )
            after = today - self.today
            if after.days > 0:
                self.today = today
                today_str = datetime.today().astimezone(nyc).strftime('%Y-%m-%d')
                calendar = alpaca.getMarketCalendar(today_str)
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
                self.__prepareWatcher(current_dt, market_open, market_close)
            time.sleep(60*60*4)
