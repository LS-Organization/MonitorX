import os
from dotenv import load_dotenv
import requests

load_dotenv()
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_alert(message: str):
    try:
        r = requests.post(SLACK_WEBHOOK_URL, json={"text": message})
        if r.status_code != 200:
            print(f"Slack error: {r.status_code} {r.text}")
    except Exception as e:
        print(f"Slack exception: {e}")

