from flask_mysqldb import MySQL, MySQLdb
from flask import Flask, request, redirect
app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "database"
#app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123_Nemam_zadne_heslo@127.0.0.1/users"

mysql = MySQL(app)