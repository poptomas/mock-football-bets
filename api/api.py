from flask import Flask, request, redirect
from flask.templating import render_template
from flask_mysqldb import MySQL, MySQLdb

import bcrypt
import os

app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "123_Nemam_zadne_heslo"
app.config["MYSQL_DB"] = "database"

app.config["SECRET_KEY"] = os.urandom(16)
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123_Nemam_zadne_heslo@127.0.0.1/users"

mysql = MySQL(app)

@app.route('/', methods = ["POST", "GET"])
def home():
    return render_template("index.html")

@app.route('/login', methods = ["POST", "GET"])
def login():
    return render_template("login.html")

@app.route("/register", methods = ["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"].encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cursor = mysql.connect.cursor()
        cursor.execute("CREATE DATABASE mockbets IF NOT EXISTS")
        cursor.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s), (name, email, hashed_password)")

        mysql.connection.commit()
        return redirect("/")

if __name__ == "__main__":
    app.run(host  = "localhost", port = 5000, debug = True)