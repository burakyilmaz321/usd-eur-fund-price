import os
from datetime import datetime

import requests
from flask import Flask, request, make_response
from tefas import Crawler


# pylint: disable=C0103
app = Flask(__name__)


currency_url = "http://api.exchangeratesapi.io/v1/"
currency_access_key = ""


@app.route("/")
def readme():
    with open("README.md", "r") as fstream:
        readme = fstream.read()
    return readme


@app.route("/usd")
def usd():
    date = request.args.get("date") or datetime.today().date().isoformat()
    res = requests.get(f"{currency_url}/{date}?access_key={currency_access_key}&symbols=TRY,USD")
    data = res.json()
    resp = make_response(str(data["rates"]["TRY"] / data["rates"]["USD"]))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/eur")
def eur():
    date = request.args.get("date") or datetime.today().date().isoformat()
    res = requests.get(f"{currency_url}/{date}?access_key={currency_access_key}&symbols=TRY")
    data = res.json()
    resp = make_response(str(data["rates"]["TRY"]))
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/fon")
def fund():
    fund_code = request.args.get("q")
    date = request.args.get("date") or datetime.today().date().isoformat()
    client = Crawler()
    data = client.fetch(start=date, name=fund_code, columns=["price"])
    resp = make_response(str(data.price[0]))
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


if __name__ == "__main__":
    server_port = os.environ.get("PORT", "8080")
    app.run(debug=False, port=server_port, host="0.0.0.0")
