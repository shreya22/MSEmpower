from flask import Flask
from flask import json, jsonify
app = Flask(__name__)

@app.route("/", methods = ['POST'])
def api_message():
   return jsonify({"data": "yay"})