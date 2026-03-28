\import asyncio
import websockets
import json
import os
from flask import Flask, jsonify
import threading

connected_clients = {}

# =========================
# WEBSOCKET HANDLER
# =========================

async def handle_client(websocket):
    device_id = None

    try:
        async for message in websocket:
            data = json.loads(message)

            if data.get("type") == "register":
                device_id = data.get("device_id")
                connected_clients[device_id] = websocket
                print(f"[Cloud] Device connected: {device_id}")

            elif data.get("type") == "command":
                target_id = data.get("target_id")

                if target_id in connected_clients:
                    await connected_clients[target_id].send(json.dumps(data))
                    print(f"[Cloud] Command forwarded to {target_id}")

    except:
        pass

    finally:
        if device_id and device_id in connected_clients:
            del connected_clients[device_id]
            print(f"[Cloud] Device disconnected: {device_id}")


# =========================
# FLASK APP
# =========================

app = Flask(__name__)

@app.route("/")
def home():
    return "Zephyr Cloud Running 🚀"

@app.route("/status")
def status():
    return jsonify({
        "connected_devices": list(connected_clients.keys())
    })


# =========================
# RUN SERVERS (SINGLE PORT)
# =========================

def start_flask(port):
    app.run(host="0.0.0.0", port=port)


async def start_websocket(port):
    async with websockets.serve(handle_client, "0.0.0.0", port):
        print(f"[Cloud] WebSocket running on port {port}")
        await asyncio.Future()


def main():
    port = int(os.environ.get("PORT", 10000))

    print(f"[Cloud] Running on port {port}")

    threading.Thread(target=start_flask, args=(port,), daemon=True).start()
    asyncio.run(start_websocket(port))


if __name__ == "__main__":
    main()
