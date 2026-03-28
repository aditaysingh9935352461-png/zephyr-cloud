import asyncio
import websockets
import json
from flask import Flask, request, jsonify
import threading

# =========================
# GLOBAL CONNECTION STORE
# =========================

connected_clients = {}

# =========================
# WEBSOCKET SERVER
# =========================

async def handle_client(websocket):

    device_id = None

    try:
        async for message in websocket:

            data = json.loads(message)

            # REGISTER DEVICE
            if data.get("type") == "register":
                device_id = data.get("device_id")
                connected_clients[device_id] = websocket

                print(f"[Cloud] Device connected: {device_id}")

            # FORWARD COMMAND
            elif data.get("type") == "command":

                target_id = data.get("target_id")

                if target_id in connected_clients:
                    target_ws = connected_clients[target_id]

                    await target_ws.send(json.dumps(data))

                    print(f"[Cloud] Command forwarded to {target_id}")

    except:
        pass

    finally:
        if device_id and device_id in connected_clients:
            del connected_clients[device_id]
            print(f"[Cloud] Device disconnected: {device_id}")


async def start_ws_server():
    print("[Cloud] WebSocket running on port 8765")
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever


# =========================
# HTTP SERVER (OPTIONAL)
# =========================

app = Flask(__name__)

@app.route("/status")
def status():
    return jsonify({
        "connected_devices": list(connected_clients.keys())
    })


def start_http():
    print("[Cloud] HTTP running on port 6000")
    app.run(host="0.0.0.0", port=6000)


# =========================
# MAIN
# =========================

def main():
    threading.Thread(target=start_http, daemon=True).start()
    asyncio.run(start_ws_server())


if __name__ == "__main__":
    main()