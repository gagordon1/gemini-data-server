from flask import Flask
import ssl
import websocket
import json
import base64
import hmac
import hashlib
import time

PORT=8080
app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run(debug=True, port=PORT)
