# from modal import Stub, web_endpoint
# from modal import Image, Stub, wsgi_app

# stub = Stub("hello")
# image = Image.debian_slim().pip_install("flask")


# @stub.function(image=image)
# @wsgi_app()
# def flask_app():

from flask import Flask, request, jsonify
import goodbye

app = Flask(__name__)

@app.get("/")
def home():
    return "Home!"

@app.get("/chat")
def get_msg():
    msg = request.args.get('msg', default="What?", type=str)
    return msg

@app.route("/testing/<test_id>")
def test(test_id):
    return goodbye.testing(test_id)

# return app
