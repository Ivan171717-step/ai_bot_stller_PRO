import os
import requests

URL = os.getenv("GOOGLE_SCRIPT_URL")
SECRET = os.getenv("GOOGLE_SCRIPT_SECRET")
ENABLED = os.getenv("GOOGLE_SHEETS_ENABLED") == "true"


def send_to_sheets(data_type, data):
    if not ENABLED:
        return

    try:
        payload = {
            "secret": SECRET,
            "type": data_type,
            "data": data
        }

        requests.post(URL, json=payload, timeout=5)

    except Exception as e:
        print("Sheets error:", e)