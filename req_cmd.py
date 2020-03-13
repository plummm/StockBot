import requests
import json
from datetime import datetime, timedelta
from pytz import timezone

def getDetail(symbol):
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-analysis"
    querystring = {"symbol": symbol}
    headers = {
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
        'x-rapidapi-key': "7e6fdc6e15msh194a1f2f00930e8p1a3e73jsn3594fd04b213"
    }

    count = 0
    while(count < 3):
        count += 1
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            res_json = json.loads(response.text)
            price = res_json["price"]

            if "financialData" not in res_json:
                isExist = False
                nowPrice = -1
            else:
                isExist = True
                nowPrice = res_json["financialData"]["currentPrice"]["raw"]

            detail = {
                "name":price["longName"],
                "symbol":price["symbol"],
                "currentPrice":nowPrice,
                "DailyChange":0,
                "isExist":isExist
            }
            return detail

    return {"isExist": False}


def getPrice(symbol):
    res_json = {}
    url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/stock/v2/get-analysis"
    querystring = {"symbol": symbol}
    headers = {
        'x-rapidapi-host': "apidojo-yahoo-finance-v1.p.rapidapi.com",
        'x-rapidapi-key': "7e6fdc6e15msh194a1f2f00930e8p1a3e73jsn3594fd04b213"
    }

    count = 1
    while(count<3):
        count+=1
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == 200:
            res_json = json.loads(response.text)
            break

    if "summaryDetail" in res_json:
        price = res_json["summaryDetail"]["ask"]["raw"]
    else:
        price = -1
    #if "financialData" in res_json:
    #    price = res_json["financialData"]["currentPrice"]["raw"]
    #else:
    #    price = -1
    return price

def getValidation(detail):
    return detail["isExist"]