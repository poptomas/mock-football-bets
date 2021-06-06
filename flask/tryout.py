<<<<<<< HEAD
from flask import Flask, request, url_for
from flask.templating import render_template
from werkzeug.utils import redirect
=======
from flask import Flask, request
from flask.templating import render_template
>>>>>>> api-flask-react

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

<<<<<<< HEAD

# utilities
def receive_hash_password(db_tuple):
=======
# utilities
def receive_hash_password(db_tuple):
    if is_empty(db_tuple):
        return None
>>>>>>> api-flask-react
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

<<<<<<< HEAD












=======
>>>>>>> api-flask-react
@app.route("/api/profile", methods = ["POST", "GET"])
def profile():
    return render_template("profile.html")

@app.route("/api/home")
@app.route("/api")
def home():
    return {
        "content" : "Mock football bets web application"
    }

<<<<<<< HEAD
@app.route("/api/confirmation/<token>", methods = ["POST", "GET"])
def confirmation(token):
    connection.commit()
    return render_template("home.html")

@app.route("/api/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":
        user_details = request.form
        username = user_details.get("username")

        print(username)



        email = user_details.get("email")
        password = user_details.get("password").encode("utf-8")
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
        sql_query = "INSERT INTO `users` (username, email, password) VALUES (%s, %s, %s)"
=======
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
>>>>>>> api-flask-react
        values = (username, email, hashed_password)
        try:
            cursor.execute(sql_query, values)
        except mysql.connector.IntegrityError as err:
<<<<<<< HEAD
            print("Error: {}".format(err))
        send_email(username, email)
        return {
            "status" : "sent",
            "message" : "Email sent, confirm your registration clicking the link in the email"
        }
    else:
        return render_template("register.html")

#achieved only from the email address link
@app.route("/api/confirmation", methods = ["POST", "GET"])
def confirm():
    connection.commit()
    return {
        "message" : "Registration successfully completed"
    }

@app.route("/login", methods = ["POST", "GET"])
def login():
    if request.method == "POST":
        user_details = request.form
        username = user_details.get("username")
        password = user_details.get("password").encode("utf-8")

        sql_query_get_hashed_pwd = """SELECT password FROM users WHERE username = %s"""
=======
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
>>>>>>> api-flask-react
        cursor.execute(sql_query_get_hashed_pwd, (username,)) #needs to be tuple
        users = cursor.fetchall()

        result = receive_hash_password(users)
<<<<<<< HEAD

        if bcrypt.checkpw(password, result):
            print("Login successful")
=======
        if result == None or not(bcrypt.checkpw(password, result)):
            print("invalid call")
            return {
                "status" : "invalid",
                "message" : "Credentials are incorrect"
            }
        else:
>>>>>>> api-flask-react
            return {
                "username" : username,
                "status" : "valid"
            }
<<<<<<< HEAD
        return {
            "status" : "invalid"
        }
    else:
        return render_template("login.html")
=======
    """

    

>>>>>>> api-flask-react

if __name__ == "__main__":
    app.run(debug = True)
