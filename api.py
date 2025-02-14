import time
import os
from flask import Flask, Response, request, send_from_directory

##########################################
# Load credentials from "credentials.txt"
##########################################
def read_config(filepath):
    config = {}
    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            key, val = line.split('=', 1)
            config[key.strip()] = val.strip()
    return config

cfg = read_config("credentials.txt")
INTERNAL_API_HOST = cfg["INTERNAL_API_HOST"]
USERNAME = cfg["USERNAME"]
PASSWORD = cfg["PASSWORD"]
# We won't call the router in this script. Worker does that.

##########################################
# Flask App
##########################################
app = Flask(__name__)

# Simple global cooldown to handle heavy load:
COOLDOWN_SECONDS = 2.0
last_toggle_time = 0

STATE_FILE = "current_state.txt"   # Worker updates with "0"/"1"
DESIRED_FILE = "desired_state.txt" # API writes "on"/"off" requests

@app.route("/")
def serve_index():
    # If you have an index.html in the same directory, serve it:
    return send_from_directory(".", "index.html")

@app.route("/status", methods=["GET"])
def status():
    """
    Return the current known status from current_state.txt.
    This file is updated every 20s (and upon toggles) by worker.py.
    """
    if not os.path.exists(STATE_FILE):
        return Response("Unknown", mimetype="text/plain")

    with open(STATE_FILE, "r") as f:
        current_state = f.read().strip()  # "0" or "1" or "ERR"
    return Response(current_state, mimetype="text/plain")

@app.route("/on", methods=["GET"])
def turn_on():
    global last_toggle_time
    now = time.time()

    # Enforce cooldown
    if now - last_toggle_time < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last_toggle_time))
        return Response(f"Cooldown active. Try again in ~{remaining} second(s).", mimetype="text/plain")

    # Otherwise, record the user wants "on"
    with open(DESIRED_FILE, "w") as f:
        f.write("on")

    last_toggle_time = time.time()
    return Response("OK", mimetype="text/plain")

@app.route("/off", methods=["GET"])
def turn_off():
    global last_toggle_time
    now = time.time()

    # Enforce cooldown
    if now - last_toggle_time < COOLDOWN_SECONDS:
        remaining = int(COOLDOWN_SECONDS - (now - last_toggle_time))
        return Response(f"Cooldown active. Try again in ~{remaining} second(s).", mimetype="text/plain")

    with open(DESIRED_FILE, "w") as f:
        f.write("off")

    last_toggle_time = time.time()
    return Response("OK", mimetype="text/plain")

if __name__ == "__main__":
    # Run on 0.0.0.0 for external access, e.g. behind Cloudflare Tunnel
    app.run(host="0.0.0.0", port=5000, debug=True)
