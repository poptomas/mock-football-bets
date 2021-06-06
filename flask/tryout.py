from flask import Flask, request
from flask.templating import render_template

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import random
import json

import mysql.connector
import bcrypt

app = Flask(__name__)

with open("admin.json","r") as file:
    data = json.load(file)
    connection = mysql.connector.connect(
        host = data["host"], 
        user = data["username"],
        password = data["password"],
        database = data["database"]
    )
    cursor = connection.cursor()

# utilities
def receive_hash_password(db_tuple):
    if is_empty(db_tuple):
        return None
    return "".join(db_tuple[0]).encode("utf-8")

def is_empty(storage):
    return len(storage) == 0

def generate_random(num_of_digits):
    return ''.join(["{}".format(random.randint(0, 9))for _ in range(0, num_of_digits)])

def get_email_body(username, token):
    return """<html><body>
        <p> Hello {},<br>
        in order to complete the registration to Mock Football Bets, click on the link below:<br>
        <a href="http://localhost:5000/confirmation/{}">Confirmation link</a><br><br>
        Thank you,<br>
        Mock Football Bets <p></body></html>""".format(username, token)

#email
def send_email(receiver_username, receiver_email):
    port = 465
    token = generate_random(10)
    sender_email = data["email"]
    password = data["email_password"] #an email created only for this purpose

    message = MIMEMultipart("alternative")
    message["Subject"] = "Registration Confirmation"
    message["From"] = "Mock Football Bets"
    message["To"] = receiver_email

    email_body = get_email_body(receiver_username, token)
    content = MIMEText(email_body, "html")
    message.attach(content)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

@app.route("/api/profile", methods = ["POST", "GET"])
def profile():
    return render_template("profile.html")

@app.route("/api/home")
@app.route("/api")
def home():
    return {
        "content" : "Mock football bets web application"
    }

@app.route("/confirmation/<token>", methods = ["POST", "GET"])
def confirmation(token):
    connection.commit()
    return {
        "status" : "complete",
        "message" : "Account created"
    }

@app.route("/api/register", methods = ["GET", "POST"])
def register():
    if request.method == "POST":
        user_details = request.get_json()
        username = user_details.get("username")
        email = user_details.get("email")
        password = user_details.get("password").encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

        sql_query = "INSERT INTO `users` (username, email, password) VALUES (%s, %s, %s)"        
        values = (username, email, hashed_password)
        try:
            cursor.execute(sql_query, values)
        except mysql.connector.IntegrityError as err:
            return {
                "status" : "issue",
                "message" : "Username/email already used"
            }

        send_email(username, email)
        return {
            "status" : "complete",
            "message" : "Email sent, confirm your registration clicking the link in the email"
        }
    return {
        "status" : "unchanged"
    }

import time

@app.route("/api/login", methods = ["POST", "GET"])
def login():
    return{
        "status" : time.strftime("%m/%d/%Y, %H:%M:%S", time.localtime()),
    }
    
    """
    if request.method == "POST":
        user_details = request.get_json()
        username = user_details.get("username")
        password = None
        if user_details == None:
            password = 12345
        else:
            password = user_details.get("password").encode("utf-8")
    """
        #sql_query_get_hashed_pwd = """SELECT password FROM users WHERE username = %s"""
    """
        cursor.execute(sql_query_get_hashed_pwd, (username,)) #needs to be tuple
        users = cursor.fetchall()

        result = receive_hash_password(users)
        if result == None or not(bcrypt.checkpw(password, result)):
            print("invalid call")
            return {
                "status" : "invalid",
                "message" : "Credentials are incorrect"
            }
        else:
            return {
                "username" : username,
                "status" : "valid"
            }
    """

    


if __name__ == "__main__":
    app.run(debug = True)
