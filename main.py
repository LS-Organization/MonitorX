import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
from dispatcher import dispatch_to_features

load_dotenv()

WS_URI = os.getenv("WS_URI")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

async def connect_and_listen():
    async with websockets.connect(WS_URI, ping_interval=None) as ws:
        print("Connected to WebSocket")

        if USERNAME and PASSWORD:
            await ws.send(json.dumps({"username": USERNAME, "password": PASSWORD}))
            print("Auth sent")

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                pos_data = data.get("pos", {})
                await dispatch_to_features(pos_data)
            except Exception as e:
                print("Error:", e)

if __name__ == "__main__":
    asyncio.run(connect_and_listen())
