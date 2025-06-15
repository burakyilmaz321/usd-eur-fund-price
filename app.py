import os
from datetime import datetime, timedelta

import pandas as pd
import redis
import requests
from flask import Flask, request, make_response
from tefas import Crawler


# pylint: disable=C0103
app = Flask(__name__)


# Load dotenv
try:
    with open(".env", "r") as fstream:
        lines = fstream.read().split()
    os.environ.update({line.split("=")[0]: line.split("=")[1] for line in lines})
except FileNotFoundError:
    print("Cannot find .env file. Skipping...")


currency_url = "http://api.exchangeratesapi.io/v1/"
currency_access_key = os.getenv("API_KEY")
upstash_redis_url = os.getenv("UPSTASH_REDIS_URL")


def get_cached_price(crawler_client, fund_code, date):
    """Get price from KV first, if does not exist, get from Tefas"""

    # Set up Redis connection
    r = redis.Redis.from_url(upstash_redis_url)

    # create a unique key for this fund_code and date combination
    key = f"{fund_code}_{date}"

    # check if price exists in cache
    price = r.get(key)

    if price is not None:
        print("Returning from cache")
        # check if price is the placeholder for None
        if price.decode("utf-8") == "None":
            return None
        else:
            # convert bytes to float
            return float(price.decode("utf-8"))

    # if price is not in cache, fetch from Tefas
    data = crawler_client.fetch(start=date, name=fund_code, columns=["price"])

    if data.empty:
        # cache a placeholder for None in Redis
        r.set(key, "None")
        return None
    else:
        # cache the price in Redis for future use
        price_data = float(data.price[0])
        r.set(key, price_data)
        return price_data


@app.route("/")
def readme():
    with open("README.md", "r") as fstream:
        readme = fstream.read()
    return readme


@app.route("/usd")
def usd():
    date = request.args.get("date") or datetime.today().date().isoformat()
    res = requests.get(
        f"{currency_url}/{date}?access_key={currency_access_key}&symbols=TRY,USD"
    )
    data = res.json()
    resp = make_response(str(data["rates"]["TRY"] / data["rates"]["USD"]))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/eur")
def eur():
    date = request.args.get("date") or datetime.today().date().isoformat()
    res = requests.get(
        f"{currency_url}/{date}?access_key={currency_access_key}&symbols=TRY"
    )
    data = res.json()
    resp = make_response(str(data["rates"]["TRY"]))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/fon")
def fund():
    fund_code = request.args.get("q")
    if not fund_code:
        return "Fund code parameter is required.", 400

    date = request.args.get("date") or datetime.today().date().isoformat()
    client = Crawler()
    # try fetch until there's data for given day, bail out when max_attempt is reached
    max_attempt, attempt_count, is_empty = 5, 0, True
    while is_empty:
        if max_attempt == attempt_count:
            break
        fetch_date = (
            (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=attempt_count))
            .date()
            .isoformat()
        )
        print(f"Try fetch for fund: {fund_code}, date: {fetch_date}")
        price = get_cached_price(client, fund_code, fetch_date)
        is_empty = price is None
        attempt_count += 1
    resp = make_response(str(price))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/all")
def all_funds():
    date = request.args.get("date") or datetime.today().date().isoformat()
    client = Crawler()
    data = client.fetch(start=date, columns=["code", "title", "price"])
    resp = make_response(data.to_csv(index=False))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route("/multi")
def multi():
    fund_code = request.args.getlist("q")
    decimal = request.args.get("dec")
    date = request.args.getlist("date") or [datetime.today().date().isoformat()]
    client = Crawler()
    data = client.fetch(
        start=min(date), end=max(date), columns=["code", "date", "price"]
    )
    data = data[
        data["code"].isin(fund_code)
        & data["date"].isin(
            map(lambda d: datetime.strptime(d, "%Y-%m-%d").date(), date)
        )
    ]
    resp = make_response(data.to_csv(index=False, decimal=decimal if decimal else "."))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route("/returns")
def returns():
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": "https://www.tefas.gov.tr",
        "Referer": "https://www.tefas.gov.tr/FonKarsilastirma.aspx",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = {
        "calismatipi": "2",
        "fontip": "YAT",
        "sfontur": "",
        "kurucukod": "",
        "fongrup": "",
        "bastarih": (datetime.today() - timedelta(days=30)).date().strftime("%d.%m.%Y"),
        "bittarih": datetime.today().date().strftime("%d.%m.%Y"),
        "fonturkod": "",
        "fonunvantip": "",
        "strperiod": "1,1,1,1,1,1,1",
        "islemdurum": "",
    }
    response = requests.post(
        "https://www.tefas.gov.tr/api/DB/BindComparisonFundReturns",
        headers=headers,
        data=data,
    )
    fund_returns_response = response.json()["data"]
    response = requests.post(
        "https://www.tefas.gov.tr/api/DB/BindComparisonFundSizes",
        headers=headers,
        data=data,
    )
    fund_sizes_response = response.json()["data"]
    fund_returns_df = pd.DataFrame(fund_returns_response)
    fund_sizes_df = pd.DataFrame(fund_sizes_response)
    fund_sizes_df = fund_sizes_df[["FONKODU", "FONTURACIKLAMA"]]
    fund_sizes_df = fund_sizes_df.rename(columns={"FONTURACIKLAMA": "unvan_tipi"})
    fund_returns_df = fund_returns_df.merge(fund_sizes_df, on=["FONKODU"])
    fund_returns_df = fund_returns_df.rename(
        columns={
            "FONKODU": "kod",
            "FONUNVAN": "isim",
            "FONTURACIKLAMA": "tip",
            "GETIRI1A": "getiri_1a",
            "GETIRI3A": "getiri_3a",
            "GETIRI6A": "getiri_6a",
            "GETIRI1Y": "getiri_1y",
            "GETIRIYB": "getiri_yb",
            "GETIRI3Y": "getiri_3y",
            "GETIRI5Y": "getiri_5y",
        }
    )
    fund_returns_df["getiri_1a"] = fund_returns_df["getiri_1a"] / 100
    fund_returns_df["getiri_3a"] = fund_returns_df["getiri_3a"] / 100
    fund_returns_df["getiri_6a"] = fund_returns_df["getiri_6a"] / 100
    fund_returns_df["getiri_1y"] = fund_returns_df["getiri_1y"] / 100
    fund_returns_df["getiri_yb"] = fund_returns_df["getiri_yb"] / 100
    fund_returns_df["getiri_3y"] = fund_returns_df["getiri_3y"] / 100
    fund_returns_df["getiri_5y"] = fund_returns_df["getiri_5y"] / 100
    fund_returns_df = fund_returns_df[
        [
            "kod",
            "isim",
            "tip",
            "unvan_tipi",
            "getiri_1a",
            "getiri_3a",
            "getiri_6a",
            "getiri_1y",
            "getiri_yb",
            "getiri_3y",
            "getiri_5y",
        ]
    ]
    resp = make_response(fund_returns_df.to_csv(index=False))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Content-Type"] = "text/csv"
    return resp


@app.route("/value")
def value():
    fund_codes = request.args.get("fund")
    shares = request.args.get("shares")
    date = request.args.get("date") or datetime.today().date().isoformat()

    if not fund_codes or not shares:
        return "Fund codes and shares parameters are required.", 400

    fund_codes = fund_codes.split(",")
    shares = list(map(int, shares.split(",")))

    if len(fund_codes) != len(shares):
        return "Fund codes and shares list lengths do not match.", 400

    client = Crawler()
    total_value = 0
    for fund_code, share in zip(fund_codes, shares):
        # try fetch until there's data for given day, bail out when max_attempt is reached
        max_attempt, attempt_count, is_empty = 5, 0, True
        while is_empty:
            if max_attempt == attempt_count:
                break
            fetch_date = (
                (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=attempt_count))
                .date()
                .isoformat()
            )
            print(f"Try fetch for fund: {fund_code}, date: {fetch_date}")
            price = get_cached_price(client, fund_code, fetch_date)
            is_empty = price is None
            attempt_count += 1
        total_value += price * share
    resp = make_response(str(total_value))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


if __name__ == "__main__":
    server_port = os.environ.get("PORT", 8080)
    app.run(debug=False, port=int(server_port), host="0.0.0.0")
