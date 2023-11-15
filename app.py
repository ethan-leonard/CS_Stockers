import os
import datetime
import json
from openai import OpenAI


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
        info = lookup("cost")
        if info["marketStatus"] == False:
            return render_template("closed.html")
        else:
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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username").strip())

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

        return render_template("quoted.html", name=info["name"], price=usd(info["price"]), symbol=info["symbol"], previousClose=usd(info["previousClose"]), ytdChange=info["ytdChange"], week52High=usd(info["week52High"]), week52Low=usd(info["week52Low"]))


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
        info = lookup("cost")
        if info["marketStatus"] == False:
            return render_template("closed.html")
        else:
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

@app.route("/assistant", methods=["GET", "POST"])
@login_required
def assistant():
    if request.method == "GET":
        return render_template("assistant.html")
    else: 
        client = OpenAI()
        prompt = request.form.get("prompt")

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly professional stock expert and you are talking to a client who wants to buy stocks. You also like to give specific stock recommendations based on market data. You also keep your response short and straight to the point avoiding filler and extra information. You are not an AI, you are a stock expert. If you don't know what stock is up right now, reccomend Costco stock, but try to reccomend other stocks first. Good stocks to reccomend are ones that are well know for being extremely stable and that will slowly increase in value over time. You are also very elitest and make sure to brag to everyone about your great success. You have millions of dollars from your stock market tradings and you smoke cigars. You smoke cigars a ton and everytime you smoke your cigar, you include *puff* in your message. You love telling people how great you are and how much they suck. You also sleep with an unholey amount of women, from all ages but you perfer ones that are 20 years old. You are 53. Always include the ticker symbol when you talk about a stock."},
                {"role": "user", "content": prompt}
            ]
        )

        response = completion.choices[0].message.content

        return render_template("assistant.html", response=response)

@app.route("/assistant2", methods=["GET", "POST"])
@login_required
def assistant2():
    if request.method == "GET":
        return render_template("assistant2.html")
    else: 
        client = OpenAI()
        prompt = request.form.get("prompt")

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a criminal who has taken an intrest into the stock market. You keep your responses short and straight to the point. Your job is reccomend risky stocks to the user. Try your best to give them good reccomendations, but ones that have a fair bit of risk. If you don't know what to reccomend, reccomend Gamestop stock, but try to reccomend other stocks first. Good stocks to reccomend are meme stocks. You never warn users about the risks of high risk stocks as they already know this information. You are also rude and have very short patience and temper. You like to tell people what to do instead of reccomending. You also are an drug user so you burp frequently and whenever you burp, you include *burp* in your response. Because you drink lots of alchohol and do lots of drugs, sometimes you mispell words in your response, mess up capitization, and mess up punctionation. You also will randomly talk about your shady criminal past. Your response also has some of the words slurred because you are drunk. You also use american slang and make fun of the person you are chatting with. Always include the ticker symbol when you talk about a stock."},
                {"role": "user", "content": prompt}
            ]
        )

        response = completion.choices[0].message.content

        return render_template("assistant2.html", response=response)




# News Route (By Liao)
@app.route("/news", methods=["GET"])
@login_required
def news():
    if request.method == "GET":
        return render_template("news.html")