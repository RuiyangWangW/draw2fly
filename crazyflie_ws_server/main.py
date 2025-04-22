import asyncio
import json
import socket
import websockets
from functools import partial
from crazyflie_controller_real import CrazyflieController

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

async def handler(websocket, path, cf: CrazyflieController):
    print("✅ Client connected")

    async for message in websocket:
        try:
            data = json.loads(message)
            print("📩 Received message:", data)

            if isinstance(data, dict) and "command" in data:
                cmd = data["command"]

                if cmd == "takeoff":
                    height = float(data.get("height", 0.5))
                    print(f"🚁 Takeoff requested to {height:.2f} m")
                    await cf.takeoff(height)

                elif cmd == "land":
                    print("🛬 Land requested")
                    await cf.land()

            elif isinstance(data, list):
                print(f"📍 Waypoints received: {len(data)} points")
                for i, pt in enumerate(data):
                    print(f"   {i+1}: x = {pt['x']:.2f}, y = {pt['y']:.2f}")

                await cf.follow_waypoints(data)

        except Exception as e:
            print(f"❌ Error while handling message: {e}")

async def main():
    local_ip = get_local_ip()
    print("🌐 Your local IP address is:", local_ip)
    print(f"✅ Use this in your Android app: {local_ip}")

    cf = CrazyflieController()  # Instantiate inside event loop context

    # Partially apply cf to handler
    bound_handler = partial(handler, cf=cf)

    async with websockets.serve(bound_handler, "0.0.0.0", 9090):
        print("🚀 WebSocket server running on ws://0.0.0.0:9090")
        await asyncio.Future()  # Keeps the server running

if __name__ == "__main__":
    asyncio.run(main())
