from flask import Flask, request
from werkzeug.utils import redirect

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import random
import json
import bcrypt

import mysql.connector
from mysql.connector.errors import Error

app = Flask(__name__)

#estabilish connection with db
with open("credentials.json","r") as file:
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

#email
def get_email_body(username, token):
    return """<html><body>
        <p> Hello {},<br>
        in order to complete the registration to Mock Football Bets, click on the link below:<br>
        <a href="http://localhost:5000/confirmation/{}">Confirmation link</a>, no additional action required.<br><br>
        Thank you<br>
        Mock Football Bets <p></body></html>""".format(username, token)

def send_email(recipient_username, recipient_email):
    port = 465
    token = generate_random(10)
    sender_email = data["email"]
    password = data["email_password"]

    message = MIMEMultipart("alternative")
    message["Subject"] = "Registration Confirmation"
    message["From"] = "Mock Football Bets"
    message["To"] = recipient_email

    email_body = get_email_body(recipient_username, token)
    content = MIMEText(email_body, "html")
    message.attach(content)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        try:
            server.sendmail(sender_email, recipient_email, message.as_string())
        except:
            raise Error("Email could not be sent - recipient unknown")


#routes
@app.route("/confirmation/<token>", methods = ["POST", "GET"])
def confirmation(token):
    connection.commit()
    #print("Account successfully created")
    return redirect("http://localhost:3000/login")

@app.route("/api/register", methods = ["GET", "POST"])
def register():
    if is_empty(request.data):
        return { }
    user_details = json.loads(request.data)
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

@app.route("/api/login", methods = ["POST", "GET"])
def login():
    if is_empty(request.data):
        return { }
    user_details = json.loads(request.data)
    username = user_details.get("username")
    password = user_details.get("password").encode("utf-8")
    sql_query_get_hashed_pwd = """SELECT password FROM users WHERE username = %s"""
    cursor.execute(sql_query_get_hashed_pwd, (username,)) #needs to be tuple
    users = cursor.fetchall()
    result = receive_hash_password(users)
    if not(result) or not(bcrypt.checkpw(password, result)):
        return {
            "status" : "invalid",
            "message" : "Credentials are incorrect"
        }
    else:
        return {
            "username" : username,
            "status" : "valid",
            "message" : "Welcome back"
        }

if __name__ == "__main__":
    app.run(debug = True)
