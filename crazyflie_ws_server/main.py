import asyncio
import json
import websockets
from crazyflie_controller import CrazyflieController
import socket

# Optional: mock mode (set to False when flying for real)
cf = CrazyflieController()

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # connect to a public IP, doesn't actually send data
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

async def handler(websocket):
    print("✅ Client connected")

    async for message in websocket:
        try:
            data = json.loads(message)
            print("📩 Received message:", data)

            if isinstance(data, dict) and "command" in data:
                cmd = data["command"]
                if cmd == "takeoff":
                    height = float(data.get("height", 1.0))
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
    print(f"✅ Use this in your Android app: 10.0.2.2")
    async with websockets.serve(handler, "0.0.0.0", 9090):
        print("🚀 WebSocket server running on ws://0.0.0.0:9090")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
