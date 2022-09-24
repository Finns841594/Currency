
from flask import Flask, render_template, request, redirect, flash, session
import psycopg2
from psycopg2 import sql
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import requests
from datetime import date as datef
from decimal import *
import os
from dotenv import load_dotenv

# Functions I wrote
from cos_tools import *


# Configure application
app = Flask(__name__)
if __name__ == "__main__":
    app.run(debug=True)

# Auto-reload templates
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem ?
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect Postgresql
# conn = psycopg2.connect(database="currency", user = "postgres", password = "guess", host = "localhost", port = "5432")
load_dotenv()
DBNAME = os.getenv("DBNAME")
DBHOST = os.getenv("DBHOST")
DBUSER = os.getenv("DBUSER")
DBPASS = os.getenv("DBPASS")
API3 = os.getenv("API3")
conn = psycopg2.connect(database=DBNAME, user = DBUSER, password = DBPASS, host = DBHOST, port = "5432")
conn.autocommit = True 
cursor = conn.cursor()

# Create Default Tabble
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
               (id SERIAL PRIMARY KEY NOT NULL UNIQUE, 
                username TEXT NOT NULL UNIQUE, 
                hash TEXT NOT NULL, 
                reg_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                prefer_currencies TEXT[],
                base_currency TEXT);''')

cursor.execute('''CREATE TABLE IF NOT EXISTS exchangerates(
                id SERIAL PRIMARY KEY NOT NULL UNIQUE,
                date TEXT,
                rates JSONB);''')

# Getting currency names:
base_currency = "CNY"
url_cur_fullname = f"https://openexchangerates.org/api/currencies.json"
cur_fullname_list = requests.get(url_cur_fullname).json()

# VARIABLES: for each users
prefer_currencies = []

@app.route("/")
def index():
    """Current Currency Rate"""
    today = str(datef.today())
    rates = get_rates_with_recoreding(today)
    cur_list = list(rates.keys())

    # Get the base currency:
    try:
        username = session["user_name"]
        cursor.execute("SELECT base_currency FROM users WHERE username = %s;",(username,))
        result = cursor.fetchall()
        if result[0][0] == None:
            base_currency = "CNY"
        else:
            base_currency = result[0][0]
    except:
        base_currency = "USD"
  
    return render_template("index.html", rates=rates, cur_names=cur_fullname_list,base_currency=base_currency, today=today)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register"""
    if request.method == "POST":
        
        # Input Check:
        # Input a username:
        if not request.form.get("username"):
            message = "must provide username"
            flash(message)
            return render_template("register.html")
        # Check if the name is already existed
        username = request.form.get("username") # username is a string
        cursor.execute("SELECT * FROM users WHERE username=%s;", (username,))
        if len(cursor.fetchall()) == 1:
            message = "The user name has been taken"
            flash(message)
            return render_template("register.html")
        # Check if there is a password
        elif not request.form.get("password"):
            message = "must provide password"
            flash(message)
            return render_template("register.html")
        # Check if there is a repeated password
        elif not request.form.get("confirmation"):
            message = "must type in password twice"
            flash(message)
            return render_template("register.html")
        # Check if both password inputs are the same
        elif not request.form.get("password") == request.form.get("confirmation"):
            message = "passwords typed in are not the same"
            flash(message)
            return render_template("register.html")

        # Register Account:
        # Password Record:
        password = request.form.get("password")
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        # Register in the users table
        cursor.execute("INSERT INTO users(username, hash) VALUES(%s, %s);", (username, hash))
        # Create a table for the new user:
        cursor.execute(sql.SQL('''CREATE TABLE IF NOT EXISTS {} (
            tran_id SERIAL PRIMARY KEY NOT NULL UNIQUE,
            amount NUMERIC(10,2),
            currency TEXT,
            tran_time DATE DEFAULT CURRENT_DATE
            );''').format(sql.Identifier(username)))
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log in"""

    session.clear()

    if request.method == "POST":

        # Check users input:
        if not request.form.get("username"):
            message = "must provide username"
            flash(message)
            return render_template("login.html")
        elif not request.form.get("password"):
            message = "must provide password"
            flash(message)
            return render_template("login.html")

        # Check username and password pairs:
        username = request.form.get("username")
        password = request.form.get("password")
        cursor.execute("SELECT * FROM users WHERE username = %s;", (username,))
        rows = cursor.fetchall()
        if len(rows) != 1 or not check_password_hash(rows[0][2], password):
            message = "wrong user name or password"
            flash(message)
            return render_template("login.html")

        # If all tests above are past, record in session and return to index page:
        session["user_id"] = rows[0][0]
        session["user_name"] = rows[0][1]
        return redirect("/mbk")

    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/mbk", methods=["GET", "POST"])
def mbk():
    """Bookkeeping list page"""
    # Get the username, prefer_currecnies
    username = session["user_name"]
    cursor.execute("SELECT prefer_currencies FROM users WHERE username = %s;",(username,))
    result = cursor.fetchall()
    if result[0][0] == None:
        prefer_currencies = []
    else:
        prefer_currencies = result[0][0]

    # Get the base currency:
    cursor.execute("SELECT base_currency FROM users WHERE username = %s;",(username,))
    result = cursor.fetchall()
    if result[0][0] == None:
        base_currency = "CNY"
    else:
        base_currency = result[0][0]
    
    # Display saved informations
    cursor.execute(sql.SQL("SELECT * FROM {}").format(sql.Identifier(username)))
    history = cursor.fetchall()
    today = str(datef.today())

    if request.method == "POST":

        # Record the new information
        if request.form.get("amount"):
            amount = request.form.get("amount")
            currency = request.form.get("currency")
            # Make it possible that record without selecing the date
            if not request.form.get("date"):                
                get_rates_with_recoreding(today)
                cursor.execute(sql.SQL("INSERT INTO {} (amount, currency) VALUES (%s, %s)").format(sql.Identifier(username)),(amount, currency))
            else:
                date = request.form.get("date")
                get_rates_with_recoreding(date)
                cursor.execute(sql.SQL("INSERT INTO {} (amount, currency, tran_time) VALUES (%s, %s, %s)").format(sql.Identifier(username)),(amount, currency, date))

        # OR delete one recoreded item
        else:
            rmv_id = request.form.get("remove")
            cursor.execute(sql.SQL("DELETE FROM {} WHERE tran_id = %s").format(sql.Identifier(username)),(rmv_id,))
            
        return redirect("/mbk")
    
    # Caculate the sum
    cursor.execute(sql.SQL("SELECT amount, currency, tran_time FROM {};").format(sql.Identifier(username)))
    userdata = cursor.fetchall()
    sum = 0
    for i in range(len(userdata)):
        sum = sum + userdata[i][0] / Decimal(lookup_history_rates(userdata[i][1],userdata[i][2])) * Decimal(lookup_history_rates(base_currency,userdata[i][2]))
    # Fomulate
    sum = Decimal(sum).quantize(Decimal('0.01')) 

    return render_template("mbk.html",prefer_currencies=prefer_currencies, history=history, sum=sum, base_currency=base_currency, today=today)

@app.route("/favcur", methods=["GET", "POST"])
def favcur():
    """Alow the user to pick favorite currency for easier noting"""

    # Get the preferen currencies
    username = session["user_name"]
    cursor.execute("SELECT prefer_currencies FROM users WHERE username = %s;",(username,))
    result = cursor.fetchall()
    if result[0][0] == None:
        prefer_currencies = []
    else:
        prefer_currencies = result[0][0]

    # Get the base currency:
    cursor.execute("SELECT base_currency FROM users WHERE username = %s;",(username,))
    result = cursor.fetchall()
    if result[0][0] == None:
        base_currency = "CNY"
    else:
        base_currency = result[0][0]
    
    # Get the rates of today
    today = str(datef.today())
    rates = get_rates_with_recoreding(today)

    if request.method == "POST": 
        # Get the preferences and add the newest choice 
        if request.form.get("addtofav"):
            fav_cur = request.form.get("addtofav")       
            prefer_currencies.append(fav_cur)
            cursor.execute("UPDATE users SET prefer_currencies = %s WHERE username = %s;", (prefer_currencies, username))
        elif request.form.get("removefromfav"):
            rmv_cur = request.form.get("removefromfav")
            prefer_currencies.remove(rmv_cur)
            cursor.execute("UPDATE users SET prefer_currencies = %s WHERE username = %s;", (prefer_currencies, username))
        elif request.form.get("base_currency"):
            base_currency = request.form.get("base_currency")
            cursor.execute("UPDATE users SET base_currency = %s WHERE username = %s;", (base_currency, username))

        return redirect("/favcur")

    return render_template("favcur.html",rates=rates, cur_names=cur_fullname_list, base_currency=base_currency, prefer_currencies=prefer_currencies)