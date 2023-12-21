import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required
from pgydata import TYPES, DEPARTS, N_HOSPITALS, W_HOSPITALS, S_HOSPITALS, E_HOSPITALS, O_HOSPITALS
from rdata import NN_HOSPITALS, WW_HOSPITALS, SS_HOSPITALS, EE_HOSPITALS, OO_HOSPITALS

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
UPLOAD_FOLDER = os.path.join(app.root_path, 'file')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///medinfo.db")


@app.route('/file/<filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
        if session["user_id"] is None:
            return render_template("login.html")
        else:
            row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
            name = row["username"]
            return render_template ("index.html", name=name)

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Username needed", 100)
        elif not request.form.get("password"):
            return apology("Password needed", 101)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username or password", 102)

        session["user_id"] = rows[0]["id"]

        return redirect("/")

    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Username needed", 200)

        if not request.form.get("password"):
            return apology("Password needed", 201)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Incompatible password", 203)

        hash = generate_password_hash(request.form.get("password"))
        try:
            new_user = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", request.form.get("username"), hash)
        except:
            return apology("Username already exists", 204)
        session["user_id"] = new_user
        return redirect("/")

    else:
        return render_template("register.html")
    
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        if request.form.get("DATETIME"):
            DATETIME = request.form.get("DATETIME").replace('T', ' ')
        else:
            DATETIME = request.form.get("DATETIME")
        if request.form.get("DEPART"):
            DEPART = request.form.get("DEPART")
        else:
            return apology("Department, Type, Hospital are required", 300)
        if request.form.get("TYPE"):
            TYPE = request.form.get("TYPE")
        else:
            return apology("Department, Type, Hospital are required", 301)
        if request.form.get("HOSPITAL"):
            HOSPITAL = request.form.get("HOSPITAL")
        else:
            return apology("Department, Type, Hospital are required", 302)
        NUMBER = request.form.get("NUMBER")
        PLACE = request.form.get("PLACE")
        LINK = request.form.get("LINK")
        DEADLINE = request.form.get("DEADLINE")
        OTHER = request.form.get("OTHER")
        db.execute("INSERT INTO info (datetime,depart,type,hospital,number,place,link,deadline,other,id) VALUES (?,?,?,?,?,?,?,?,?,?)", 
                   DATETIME,DEPART,TYPE,HOSPITAL,NUMBER,PLACE,LINK,DEADLINE,OTHER,session["user_id"])
        UNIQUE = db.execute("SELECT last_insert_rowid()")[0]["last_insert_rowid()"]

        FILE = request.files['fileInput']
        if FILE:
            filename, file_extension = os.path.splitext(FILE.filename)

            unique_filename = str(UNIQUE) + file_extension

            db.execute("UPDATE info SET file = ? WHERE key = ?", unique_filename, UNIQUE)

            FILE.save(os.path.join(UPLOAD_FOLDER, unique_filename))

        return redirect("/history")

    else:
        return render_template("add.html", 
                               TYPES=TYPES, 
                               DEPARTS=DEPARTS, 
                               N_HOSPITALS=N_HOSPITALS,
                               W_HOSPITALS=W_HOSPITALS,
                               S_HOSPITALS=S_HOSPITALS,
                               E_HOSPITALS=E_HOSPITALS,
                               O_HOSPITALS=O_HOSPITALS)
  
@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    if request.method == "POST":
        return redirect("/")

    else:
        row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
        name = row["username"]
        HISTORYS = db.execute("SELECT * FROM info ORDER BY datetime DESC")
        return render_template("history.html", 
                               TYPES=TYPES, 
                               DEPARTS=DEPARTS, 
                               N_HOSPITALS=N_HOSPITALS,
                               W_HOSPITALS=W_HOSPITALS,
                               S_HOSPITALS=S_HOSPITALS,
                               E_HOSPITALS=E_HOSPITALS,
                               O_HOSPITALS=O_HOSPITALS,
                               HISTORYS=HISTORYS,
                               name=name)
    
@app.route("/delete", methods=["POST"])
@login_required
def delete():
    if request.method == "POST":
        KEY = request.form.get("KEY")
        db.execute("DELETE FROM info WHERE key = ?", (KEY,))
        return redirect("/your")
    
@app.route("/modify", methods=["GET", "POST"])
@login_required
def modify():
    if request.method == "POST":
        KEY = request.form.get("KEY")
        MODIFY = db.execute("SELECT * FROM info WHERE key = ?", (KEY,))[0]
        MTIME = MODIFY["datetime"].replace(' ', 'T')
        MDEAD = MODIFY["deadline"]
        return render_template("modify.html", 
                               MODIFY=MODIFY,
                               MTIME=MTIME,
                               MDEAD=MDEAD,
                               KEY=KEY,
                               TYPES=TYPES, 
                               DEPARTS=DEPARTS, 
                               N_HOSPITALS=N_HOSPITALS,
                               W_HOSPITALS=W_HOSPITALS,
                               S_HOSPITALS=S_HOSPITALS,
                               E_HOSPITALS=E_HOSPITALS,
                               O_HOSPITALS=O_HOSPITALS)
    if request.method == "GET":
        KEY = request.args.get("KEY")
        MODIFY = db.execute("SELECT * FROM info WHERE key = ?", (KEY,))[0]
        MTIME = MODIFY["datetime"].replace(' ', 'T')
        MDEAD = MODIFY["deadline"]
        return render_template("modify.html", 
                               MODIFY=MODIFY,
                               MTIME=MTIME,
                               MDEAD=MDEAD,
                               KEY=KEY,
                               TYPES=TYPES, 
                               DEPARTS=DEPARTS, 
                               N_HOSPITALS=N_HOSPITALS,
                               W_HOSPITALS=W_HOSPITALS,
                               S_HOSPITALS=S_HOSPITALS,
                               E_HOSPITALS=E_HOSPITALS,
                               O_HOSPITALS=O_HOSPITALS)

@app.route("/send", methods=["POST"])
@login_required
def send():
    if request.method == "POST":
        KEY = request.form.get("KEY")
        action = request.form.get("action")

        if request.form.get("DATETIME"):
            DATETIME = request.form.get("DATETIME").replace('T', ' ')
        else:
            DATETIME = request.form.get("DATETIME")
        if request.form.get("DEPART"):
            DEPART = request.form.get("DEPART")
        else:
            return apology("Department, Type, Hospital are required", 300)
        if request.form.get("TYPE"):
            TYPE = request.form.get("TYPE")
        else:
            return apology("Department, Type, Hospital are required", 301)
        if request.form.get("HOSPITAL"):
            HOSPITAL = request.form.get("HOSPITAL")
        else:
            return apology("Department, Type, Hospital are required", 302)
        NUMBER = request.form.get("NUMBER")
        PLACE = request.form.get("PLACE")
        LINK = request.form.get("LINK")
        DEADLINE = request.form.get("DEADLINE")
        OTHER = request.form.get("OTHER")

        if action == "update":

            db.execute("UPDATE info SET datetime=?, depart=?, type=?, hospital=?, number=?, place=?, link=?, deadline=?, other=?, id=? WHERE key=?", 
                    DATETIME, DEPART, TYPE, HOSPITAL, NUMBER, PLACE, LINK, DEADLINE, OTHER, session["user_id"], KEY)

            FILE = request.files['fileInput']
            if FILE:
                filename, file_extension = os.path.splitext(FILE.filename)
                unique_filename = str(KEY) + file_extension
                db.execute("UPDATE info SET file = ? WHERE key = ?", unique_filename, KEY)
                FILE.save(os.path.join(UPLOAD_FOLDER, unique_filename))

            return redirect("/your")
        
        elif action == "deletefile":
            file_to_delete = db.execute("SELECT * FROM info WHERE key=?", KEY)[0]["file"]
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], file_to_delete))
            db.execute("UPDATE info SET file = NULL WHERE key = ?", KEY)
            return redirect(url_for('modify', KEY=KEY))
        
        return redirect("/your")

@app.route("/your")
@login_required
def your():
    row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
    name = row["username"]
    HISTORYS = db.execute("SELECT * FROM info  WHERE id = ? ORDER BY datetime DESC", session["user_id"])

    return render_template("your.html", 
                            TYPES=TYPES, 
                            DEPARTS=DEPARTS, 
                            N_HOSPITALS=N_HOSPITALS,
                            W_HOSPITALS=W_HOSPITALS,
                            S_HOSPITALS=S_HOSPITALS,
                            E_HOSPITALS=E_HOSPITALS,
                            O_HOSPITALS=O_HOSPITALS,
                            HISTORYS=HISTORYS,
                            name=name)

@app.route("/pgy")
@login_required
def pgy():
    row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
    name = row["username"]
    NUMBERS = db.execute("SELECT * FROM pgy WHERE type = ? ORDER BY year DESC", "PGY")
    LINKS = db.execute("SELECT * FROM link WHERE type = ? ORDER BY year DESC", "PGY")
    return render_template("pgy.html", 
                        TYPES=TYPES, 
                        DEPARTS=DEPARTS, 
                        N_HOSPITALS=N_HOSPITALS,
                        W_HOSPITALS=W_HOSPITALS,
                        S_HOSPITALS=S_HOSPITALS,
                        E_HOSPITALS=E_HOSPITALS,
                        O_HOSPITALS=O_HOSPITALS,
                        NUMBERS=NUMBERS,
                        LINKS=LINKS,
                        name=name)

@app.route("/r")
@login_required
def r():
    row = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])[0]
    name = row["username"]
    NUMBERS = db.execute("SELECT * FROM r WHERE type = ? AND depart != ? ORDER BY year DESC", "R", "神經科")
    NEUROS = db.execute("SELECT * FROM r WHERE type = ? AND depart = ? ORDER BY year DESC", "R", "神經科")
    TOTALS = db.execute("SELECT * FROM number WHERE type = ? ORDER BY year DESC", "R")
    return render_template("r.html", 
                        TYPES=TYPES, 
                        DEPARTS=DEPARTS, 
                        NN_HOSPITALS=NN_HOSPITALS,
                        WW_HOSPITALS=WW_HOSPITALS,
                        SS_HOSPITALS=SS_HOSPITALS,
                        EE_HOSPITALS=EE_HOSPITALS,
                        OO_HOSPITALS=OO_HOSPITALS,
                        NUMBERS=NUMBERS,
                        NEUROS=NEUROS,
                        TOTALS=TOTALS,
                        name=name)
