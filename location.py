# location.py
from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

def fetch_user_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        city = data.get("city", "Unknown")
        return city
    except Exception as e:
        return "Unknown"

@app.route("/get_location", methods=["GET"])
def get_location():
    city = fetch_user_location()
    return jsonify({"city": city})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Use Railway's assigned port
    app.run(host="0.0.0.0", port=port)