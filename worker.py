import time
import requests
import os

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

# Load credentials
cfg = read_config("credentials.txt")
INTERNAL_API_HOST = cfg["INTERNAL_API_HOST"]
USERNAME = cfg["USERNAME"]
PASSWORD = cfg["PASSWORD"]

PIN = "dio1"  # Could also read from a file or handle multiple pins, if desired.

DESIRED_FILE = "desired_state.txt"
STATE_FILE = "current_state.txt"

CHECK_INTERVAL = 1       # Check desired_state.txt every 1s
STATUS_REFRESH = 20      # Also refresh the actual router state every 20s
last_status_fetch_time = 0
last_desired_state = None

def internal_on():
    url = f"http://{INTERNAL_API_HOST}/cgi-bin/io_state"
    params = {"username": USERNAME, "password": PASSWORD, "pin": PIN, "state": "on"}
    return requests.get(url, params=params, timeout=5).text.strip()

def internal_off():
    url = f"http://{INTERNAL_API_HOST}/cgi-bin/io_state"
    params = {"username": USERNAME, "password": PASSWORD, "pin": PIN, "state": "off"}
    return requests.get(url, params=params, timeout=5).text.strip()

def internal_value():
    url = f"http://{INTERNAL_API_HOST}/cgi-bin/io_value"
    params = {"username": USERNAME, "password": PASSWORD, "pin": PIN}
    return requests.get(url, params=params, timeout=5).text.strip()

def write_current_state(state):
    """Write '0', '1', or 'ERR' to current_state.txt."""
    with open(STATE_FILE, "w") as f:
        f.write(state)

def main():
    global last_status_fetch_time, last_desired_state

    # Initialize current state (fetch once on startup)
    try:
        init_state = internal_value()
        write_current_state(init_state)
    except Exception as e:
        print("Error on initial status fetch:", e)
        write_current_state("ERR")

    while True:
        now = time.time()

        # 1) Check if we need to refresh status from router
        if now - last_status_fetch_time > STATUS_REFRESH:
            try:
                real_state = internal_value()
                write_current_state(real_state)
            except Exception as e:
                print("Error fetching status:", e)
                write_current_state("ERR")
            last_status_fetch_time = time.time()

        # 2) Check desired_state.txt for a new toggle request
        if os.path.exists(DESIRED_FILE):
            with open(DESIRED_FILE, "r") as f:
                desired_state = f.read().strip()
        else:
            desired_state = None

        # If changed from what we last executed, perform the toggle
        if desired_state and desired_state != last_desired_state:
            if desired_state == "on":
                try:
                    result = internal_on()
                    print(f"Toggled ON -> Router returned: {result}")
                    # Also update current_state.txt if "OK"
                    if "OK" in result.upper():
                        write_current_state("1")
                except Exception as e:
                    print("Error toggling on:", e)
            elif desired_state == "off":
                try:
                    result = internal_off()
                    print(f"Toggled OFF -> Router returned: {result}")
                    if "OK" in result.upper():
                        write_current_state("0")
                except Exception as e:
                    print("Error toggling off:", e)

            # Remember we've handled this toggle
            last_desired_state = desired_state

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
