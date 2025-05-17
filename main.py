import os
import asyncio
import websockets
import json
from dispatcher import dispatch_to_features
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
WS_URI = os.getenv("WS_URI")


async def connect_and_listen():
    async with websockets.connect(WS_URI, ping_interval=None) as ws:
        print("WebSocket connected")
        if USERNAME or PASSWORD:
            await ws.send(json.dumps({"username": USERNAME, "password": PASSWORD}))
            print("Auth sent")

        while True:
            try:
                msg = await ws.recv()
                data = json.loads(msg)
                pos_data = data.get("pos", {})
                await dispatch_to_features(pos_data)
            except Exception as e:
                print("WebSocket error:", e)

if __name__ == "__main__":
    asyncio.run(connect_and_listen())
