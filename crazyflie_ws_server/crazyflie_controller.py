import time

class CrazyflieController:
    def __init__(self):
        print("🛑 [Mock Mode] Crazyflie not initialized. Running in simulation.")

    async def takeoff(self, height: float = 1.0, duration: float = 3.0):
        print(f"🚁 [Mock] Taking off to {height:.2f} meters...")
        time.sleep(duration)
        print(f"✅ [Mock] Reached {height:.2f} meters.")

    async def land(self, duration: float = 3.0):
        print("🛬 [Mock] Landing...")
        for i in range(10, -1, -1):
            z = i * 0.1
            print(f"   [Mock] Altitude: {z:.1f} m")
            time.sleep(duration / 10)
        print("🛑 [Mock] Motors stopped.")

    async def follow_waypoints(self, points):
        print(f"📍 [Mock] Executing {len(points)} waypoints:")
        for i, pt in enumerate(points):
            x = float(pt["x"])
            y = float(pt["y"])
            print(f"   {i+1}: Moving to ({x:.2f}, {y:.2f})...")
            time.sleep(0.5)
        print("✅ [Mock] Finished path.")
