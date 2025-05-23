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
    while True:
        try:
            async with websockets.connect(WS_URI, ping_interval=None) as ws:
                print("Connected to WebSocket")

                if USERNAME and PASSWORD:
                    await ws.send(json.dumps({"username": USERNAME, "password": PASSWORD}))
                    print("Auth sent")

                while True:
                    msg = await ws.recv()  
                    try:
                        data = json.loads(msg)
                        pos_data = data.get("pos", {})
                        await dispatch_to_features(pos_data)
                    except json.JSONDecodeError as e:
                        print("JSON decode error:", e)
                    except Exception as e:
                        print("Feature dispatch error:", e)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"🔌 Connection closed: code={e.code}, reason={e.reason}. Reconnecting in 5s...")
        except Exception as e:
            print(f"Unexpected connection error: {e}. Reconnecting in 5s...")

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(connect_and_listen())
