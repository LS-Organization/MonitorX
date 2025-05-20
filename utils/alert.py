import os
import requests

def send_alert(message):
    webhook = os.getenv("SLACK_WEBHOOK_URL")  # 每次调用时动态获取
    if not webhook:
        print("⚠️ No SLACK_WEBHOOK_URL configured")
        return
    try:
        response = requests.post(webhook, json={"text": message})
        if response.status_code != 200:
            print("⚠️ Slack error:", response.status_code, response.text)
    except Exception as e:
        print("⚠️ Alert error:", e)
