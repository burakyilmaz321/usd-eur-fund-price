import os
from datetime import datetime, timedelta

import requests
from flask import Flask, request
from tefas import Crawler


# pylint: disable=C0103
app = Flask(__name__)


currency_url = "http://api.exchangeratesapi.io/v1/"
currency_access_key = ""


@app.route("/usd")
def usd():
    today = datetime.today().date().isoformat()
    res = requests.get(f"{currency_url}/{today}?access_key={currency_access_key}&symbols=TRY,USD")
    data = res.json()
    return str(data["rates"]["TRY"] / data["rates"]["USD"])


@app.route("/eur")
def eur():
    today = datetime.today().date().isoformat()
    res = requests.get(f"{currency_url}/{today}?access_key={currency_access_key}&symbols=TRY")
    data = res.json()
    return str(data["rates"]["TRY"])


@app.route("/fon")
def fund():
    fund_code = request.args.get("q")
    client = Crawler()
    today = datetime.today().date().isoformat()
    data = client.fetch(start=today, name=fund_code, columns=["price"])
    return str(data.price[0])


if __name__ == "__main__":
    server_port = os.environ.get("PORT", "8080")
    app.run(debug=False, port=server_port, host="0.0.0.0")
