from flask import Flask, request
from flask.templating import render_template
import os
import yaml

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(16)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:password@localhost/users"

@app.route('/login', methods = ["POST", "GET"])
def login():
    return render_template("login.html")

@app.route("/api", methods = ["GET"])
def api():
    return {
        "hello" : "sent",
        
        "man" : "up haha"
    }

if __name__ == "__main__":
    app.run(debug = True)