import os
import datetime
import json

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
#took this out for rn
#if not os.environ.get("API_KEY"):
    #raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Show portfolio of stocks"""

    user_id = session["user_id"]

    if request.method == "GET":

        transactions_data = db.execute(
            "SELECT symbol, sum(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)

        current_price = 0
        current_value = 0
        total_value = 0

        data = []

        for row in transactions_data:

            # I did shares instead of sum("shares") in couple places below which may mess it up
            stock = lookup(row["symbol"])
            current_price = stock["price"]
            current_value = current_price * row["shares"]
            data.append({"symbol": row["symbol"], "name": stock["name"], "shares": row["shares"],
                        "price": usd(current_price), "total": usd(current_value)})
            total_value += stock["price"] * row["shares"]

        funds_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        total_funds = funds_db[0]["cash"]

        total_value += total_funds

        return render_template("index.html", data=data, total=usd(total_value), cash=usd(total_funds))

    else:
        try: 
            addition = (float)(request.form.get("amount"))
        except ValueError:
            return apology("Invalid Amount")

        cash = db.execute("SELECT cash FROM users WHERE id = ?", user_id)

        money = cash[0]["cash"]

        updated_cash = money + addition

        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)

        flash("Success!")

        return redirect("/")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    user_id = session["user_id"]
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if symbol == "":
            return apology("Missing Symbol")

        info = lookup(symbol.upper())

        if info == None:
            return apology("Symbol DNE")

        if not shares.isdigit():
            return apology("Shares Must Be Whole Number")

        if int(shares) <= 0:
            return apology("Shares Must Be Positive")

        cost = info["price"] * int(shares)
        userscash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        cash = userscash[0]["cash"]


        
        transactions_data = db.execute(
            "SELECT symbol, sum(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)

        current_price = 0
        current_value = 0
        total_value = 0

        data = []

        for row in transactions_data:

            # I did shares instead of sum("shares") in couple places below which may mess it up
            stock = lookup(row["symbol"])
            current_price = stock["price"]
            current_value = current_price * row["shares"]
            data.append({"symbol": row["symbol"], "name": stock["name"], "shares": row["shares"],
                        "price": usd(current_price), "total": usd(current_value)})
            total_value += stock["price"] * row["shares"]

        total_value += cash



        if cost > cash:
            return apology("Insufficent Funds")

        newcash = cash - cost

        date = datetime.datetime.now()

        db.execute("UPDATE users SET cash=:newcash WHERE id=:id", newcash=newcash, id=session["user_id"]);

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date, sum) VALUES (:user_id, :symbol, :shares, :price, :date, :sum)",
                   user_id=session["user_id"], symbol=info['symbol'], shares=int(shares), price=info['price'], date=date, sum=total_value)

        flash("Purchased!")

        return redirect("/")


@app.route("/history")
@login_required
def history():

    user_id = session["user_id"]
    transactions_db = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)
    data = []

    for row in transactions_db:
        # I did shares instead of sum("shares") in couple places below which may mess it up
        shares = int(row["shares"])

        if shares < 0:
            method = "sold"
        else:
            method = "bought"

        data.append({"method": method, "symbol": row["symbol"], "price": row["price"],
                    "shares": row["shares"], "time": row["date"]})

    return render_template("history.html", data=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        return render_template("quote.html")

    if request.method == "POST":
        symbol = request.form.get("symbol")

        # if nothing inputed
        if symbol == "":
            return apology("Missing Symbol")

        info = lookup(symbol.upper())

        if info == None:
            return apology("Symbol DNE")

        return render_template("quoted.html", name=info["name"], price=usd(info["price"]), symbol=info["symbol"])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "GET":
        return render_template("register.html")
    else:
        # stores username, password, and comfirmation in variables
        username = request.form.get("username")
        password = request.form.get("password")
        comfirmation = request.form.get("confirmation")

        # checks to make sure all inputs are filled
        if username == "":
            return apology("Missing Username")

        if password == "":
            return apology("Missing Password")

        if comfirmation == "":
            return apology("Missing Comfirmation")

        # checks to make sure password matches comfirmation
        if password != comfirmation:
            return apology("Passwords Not the Same")

        # checks if username already exists + adds username and has to db
        try:
            hash = generate_password_hash(password)
            user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
            session["user_id"] = user
        except:
            return apology("Username Taken")

    return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():

    user_id = session["user_id"]
    

    # sell
    if request.method == "GET":
        rows = db.execute("SELECT symbol FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
        return render_template("sell.html", symbols=[row["symbol"] for row in rows])

    else:

        userscash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        cash = userscash[0]["cash"]

        transactions_data = db.execute(
            "SELECT symbol, sum(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)

        current_price = 0
        current_value = 0
        total_value = 0

        data = []
        sum = 0
        
        for row in transactions_data:

            # I did shares instead of sum("shares") in couple places below which may mess it up
            stock = lookup(row["symbol"])
            current_price = stock["price"]
            current_value = current_price * row["shares"]
            data.append({"symbol": row["symbol"], "name": stock["name"], "shares": row["shares"],
                        "price": usd(current_price), "total": usd(current_value)})
            total_value += stock["price"] * row["shares"]

            sum = cash + total_value



        symbol = request.form.get("symbol").upper()
        rows = db.execute(
            "SELECT symbol, SUM(shares) as shares FROM transactions WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
        stock = lookup(symbol)
        shares2sell = int(request.form.get("shares"))

        # User Error Checks
        if symbol == "":
            return apology("Missing Symbol")

        if shares2sell == "":
            return apology("Shares Invalid")

        if shares2sell < 0:
            return apology("Shares Invalid")

        shares = int(request.form.get("shares"))
        for row in rows:
            if row["symbol"] == symbol:
                if shares > row["shares"]:
                    return apology("Insufficent Shares")

                symbol = request.form.get("symbol")

        value = stock["price"] * shares
        userscash = db.execute("SELECT cash FROM users WHERE id=:id", id=session["user_id"])
        cash = userscash[0]["cash"]

        newcash = cash + value

        date = datetime.datetime.now()

        db.execute("UPDATE users SET cash=:newcash WHERE id=:id", newcash=newcash, id=session["user_id"])

        db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date, sum) VALUES (:user_id, :symbol, :shares, :price, :date, :sum)",
                   user_id=session["user_id"], symbol=stock['symbol'], shares=(-1*shares), price=stock['price'], date=date, sum=sum)

        flash("Sold!")

        return redirect("/")
    
@app.route("/stats", methods=["GET"])
@login_required
def stats():
    user_id = session["user_id"]
    transactions_db = db.execute("SELECT * FROM transactions WHERE user_id = ?", user_id)
    data = []

    for row in transactions_db:
        
        if row["shares"] < 0:
            # I did shares instead of sum("shares") in couple places below which may mess it up
            data.append({"time": row["date"], "sum": row["sum"]})

    return render_template("stats.html", data=data)

