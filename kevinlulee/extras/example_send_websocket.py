from __future__ import annotations
import kevinlulee as kx

from websockets.sync.client import connect
import json
def send_message(text: str, port: int = 3000):
    message = {
        "event": "message",
        "data": {
            "text": text,
            "timestamp": time.time(),
        },
    }
    with connect(f"ws://127.0.0.1:{port}") as ws:
        ws.send(json.dumps(message))

if __name__ == "__main__":
    send_message('hi')
