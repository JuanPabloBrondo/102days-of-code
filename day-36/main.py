import requests
import os
from twilio.rest import Client

STOCK_NAME = "BTC"
COMPANY_NAME = "Bitcoin"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
STOCK_API_KEY = os.environ.get("STOCK_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
account_sid = os.environ.get("account_sid")
auth_token = os.environ.get("auth_token")
MY_TWILIO_NUMBER = os.environ.get("MY_TWILIO_NUMBER")
RECIPIENT_NUMBER = os.environ.get("RECIPIENT_NUMBER")

# STEP 1: Use https://www.alphavantage.co/documentation/#daily
# When stock price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

stock_params = {
    "function": "DIGITAL_CURRENCY_DAILY",
    'symbol': STOCK_NAME,
    "apikey": STOCK_API_KEY,
    "market": "USD",
}
response = requests.get(STOCK_ENDPOINT, params=stock_params)
try:
    data = response.json()["Time Series (Digital Currency Daily)"]
    data_list = [value for (key, value) in data.items()]
    yesterday_data = data_list[0]
    yesterday_closing_price = yesterday_data["4b. close (USD)"]
    day_before_yesterday_data = data_list[1]
    day_before_yesterday_closing_price = day_before_yesterday_data["4b. close (USD)"]
except KeyError:
    day_before_yesterday_closing_price = 65000
    yesterday_closing_price = 64000

change = abs(float(day_before_yesterday_closing_price) - float(yesterday_closing_price))
dif_percent = round(change / float(day_before_yesterday_closing_price) * 100, 2)
if float(day_before_yesterday_closing_price) > float(yesterday_closing_price):
    move = "📉"
else:
    move = "🆙"

# STEP 2: https://newsapi.org/
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
if dif_percent >= 5:
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
        "pageSize": 5,
    }
    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    print(news_response.json())

    articles = news_response.json()["articles"]
    articles_filtered = []
    for article in articles[:3]:
        articles_filtered.append(
            f"\nHeadline: {article["title"]}. \nBrief: {article["description"]} \nDate: {article["publishedAt"]} \nURL: {article["url"]}")

    # STEP 3: Use twilio.com/docs/sms/quickstart/python
    # to send a separate message with each article's title and description to your phone number.

    cool_message = (f"{STOCK_NAME}: {move}{dif_percent}% "
                    f" {articles_filtered[0]}"
                    f"{articles_filtered[1]}"
                    f"{articles_filtered[2]}")
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
        body=cool_message,
        from_=MY_TWILIO_NUMBER,
        to=RECIPIENT_NUMBER
    )
