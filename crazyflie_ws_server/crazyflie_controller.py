import time
import cflib.crtp
from cflib.crazyflie import Crazyflie

class CrazyflieController:
    def __init__(self):
        # Initialize drivers
        cflib.crtp.init_drivers()
        self.uri = "radio://0/80/2M"  # Adjust to match your Crazyflie URI
        self.cf = Crazyflie()
        self.connected = False

        # Connection events
        self.cf.connected.add_callback(self._on_connected)
        self.cf.disconnected.add_callback(self._on_disconnected)
        self.cf.connection_failed.add_callback(self._on_connection_failed)
        self.cf.connection_lost.add_callback(self._on_connection_lost)

        print(f"🔌 Connecting to Crazyflie on {self.uri}...")
        self.cf.open_link(self.uri)

        # Wait for connection
        while not self.connected:
            time.sleep(0.1)

    def _on_connected(self, link_uri):
        print(f"✅ Connected to {link_uri}")
        self.connected = True

    def _on_disconnected(self, link_uri):
        print(f"🔌 Disconnected from {link_uri}")
        self.connected = False

    def _on_connection_failed(self, link_uri, msg):
        print(f"❌ Connection failed: {msg}")
        self.connected = False

    def _on_connection_lost(self, link_uri, msg):
        print(f"⚠️ Connection lost: {msg}")
        self.connected = False

    async def takeoff(self, height: float = 1.0, duration: float = 3.0):
        print(f"🚁 Taking off to {height} m")
        self.cf.commander.send_hover_setpoint(0, 0, 0, 0)
        time.sleep(0.5)

        # Ascend smoothly to target height
        self.cf.commander.send_hover_setpoint(0, 0, height, 0)
        time.sleep(duration)

    async def land(self, duration: float = 3.0):
        print("🛬 Landing")
        for i in range(10, -1, -1):
            z = i * 0.1
            self.cf.commander.send_hover_setpoint(0, 0, z, 0)
            time.sleep(duration / 10)
        self.cf.commander.send_stop_setpoint()
        print("🛑 Motors stopped")

    async def follow_waypoints(self, points):
        print(f"📍 Executing {len(points)} waypoints")
        for i, pt in enumerate(points):
            x = float(pt["x"])
            y = float(pt["y"])
            z = 1.0  # Fixed height
            print(f"   ➤ Moving to ({x:.2f}, {y:.2f}, {z:.2f})")
            self.cf.commander.send_position_setpoint(x, y, z, 0)
            time.sleep(0.5)

        # Hover at final point
        self.cf.commander.send_hover_setpoint(0, 0, 1.0, 0)
        time.sleep(1)
