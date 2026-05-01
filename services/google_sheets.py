import os
import requests

URL = os.getenv("GOOGLE_SCRIPT_URL")
SECRET = os.getenv("GOOGLE_SCRIPT_SECRET")
ENABLED = os.getenv("GOOGLE_SHEETS_ENABLED", "false").lower() == "true"


def send_to_sheets(data_type, data):
    if not ENABLED:
        print("Sheets disabled: GOOGLE_SHEETS_ENABLED is not true")
        return

    if not URL:
        print("Sheets error: GOOGLE_SCRIPT_URL is not set")
        return

    if not SECRET:
        print("Sheets error: GOOGLE_SCRIPT_SECRET is not set")
        return

    try:
        payload = {
            "secret": SECRET,
            "type": data_type,
            "data": data
        }

        response = requests.post(URL, json=payload, timeout=10)

        print("Sheets response status:", response.status_code)
        print("Sheets response text:", response.text[:500])

    except Exception as e:
        print("Sheets error:", e)