from flask import Flask
app = Flask(__name__)

@app.route("/api", methods = ["GET"])
def api():
    return {
        "hello" : "sent",
        
        "man" : "up haha"
    }

if __name__ == "__main__":
    app.run(debug = True)