import requests
from twilio.rest import Client
from datetime import datetime
import os

today = datetime.now()

date = int(str(today.date()).split("-")[2])
yesterday_date = str(today.date()).replace(str(date), str(date - 1))
day_before_yesterday = str(today.date()).replace(str(date), str(date - 2))

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

NEWS_API_KEY = os.environ.get("KEY")
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

AUTH_TOKEN = os.environ.get("AUTH_T")
AUTH_SID = os.environ.get("AUTH_S")
FRM_NO = os.environ.get("FRM_NO")
TO_NO = os.environ.get("TO_NO")

news_params = {
    "q": COMPANY_NAME,
    "from": day_before_yesterday,
    "to": yesterday_date,
    "sortBy": "popularity",
    "apiKey": NEWS_API_KEY,
}

STOCK_API_KEY = os.environ.get("STK_KEY")
STOCK_ENDPOINT = "https://www.alphavantage.co/query"

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY,
}

stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()

news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
news_response.raise_for_status()
news_data = news_response.json()

threshold_value = float(stock_data["Time Series (Daily)"][day_before_yesterday]["4. close"])
recent_value = float(stock_data["Time Series (Daily)"][yesterday_date]["4. close"])
change = round(recent_value - threshold_value, 2)
change_percentage = round(abs(change / threshold_value) * 100)
if change > 0:
    sign = "📈"
else:
    sign = "📉"

title_list = [news["title"].replace("- Reuters", "") for news in news_data["articles"][:3]]
description_list = [news["description"].replace(
    '<a href="https://www.reuters.com/companies/TSLA.O" target="_blank">(TSLA.O)</a>', "")
    for news in news_data["articles"][:3]]

if change_percentage > 1:
    client = Client(AUTH_SID, AUTH_TOKEN)

    for msg in range(len(title_list)):
        message = client.messages \
            .create(
                    body=f"{STOCK} {sign}{change_percentage}%\n\nHeadline:{title_list[msg]}\nBrief: {description_list[msg]}",
                    from_=FRM_NO,
                    to=TO_NO,
                    )
        print(message.status)
