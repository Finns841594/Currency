import requests
import urllib.parse
import psycopg2
from psycopg2.extras import Json
import os
from dotenv import load_dotenv

# Get environment variables
load_dotenv()
DBNAME = os.getenv("DBNAME")
DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPASS = os.getenv("DBPASS")
API3 = os.getenv("API3")


def get_rates(date):
    # an alternative url: url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
    api3 = API3
    url = f"https://openexchangerates.org/api/historical/{urllib.parse.quote_plus(date)}.json?app_id={urllib.parse.quote_plus(api3)}"
    print("getting rates from api: ", url)
    response = requests.get(url)
    rates_info = response.json()
    return rates_info


def get_rates_with_recoreding(date):
    conn = psycopg2.connect(database=DBNAME, user = DBUSER, password = DBPASS, host = DBHOST, port = "5432")
    cursor = conn.cursor()
    conn.autocommit = True

    # Check if the rates of the specific date has been recoreded:
    date = str(date)
    cursor.execute("SELECT * FROM exchangerates WHERE date = %s;",(date,))
    date_check = cursor.fetchall()

    # if it is not, then get the rates by api and record it.
    if not date_check:
        rates_info = get_rates(date)
        print("get rates from api", rates_info)
        rates = rates_info["rates"]
        cursor.execute("INSERT INTO exchangerates (date, rates) VALUES (%s, %s);", (date, Json(rates)))
        conn.close
        return rates
    # If it is recoreded, then read it and return it:
    else:
        cursor.execute("select rates from exchangerates where date = %s;", (date,))
        rates = cursor.fetchall()[0][0]
        conn.close
        return rates

def lookup_history_rates(currency, date):
    conn = psycopg2.connect(database=DBNAME, user = DBUSER, password = DBPASS, host = DBHOST, port = "5432")
    cursor = conn.cursor()
    date = str(date)
    cursor.execute("select rates from exchangerates where date = %s;", (date,))
    result = cursor.fetchall()[0][0][currency]
    conn.close
    return result