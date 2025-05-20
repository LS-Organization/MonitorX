import os
from dotenv import load_dotenv

load_dotenv()
print("USERNAME:", os.getenv("USERNAME"))
print("SLACK_WEBHOOK_URL:", os.getenv("SLACK_WEBHOOK_URL"))
print("WS_URI:", os.getenv("WS_URI"))
print("PASSWORD:", os.getenv("PASSWORD"))