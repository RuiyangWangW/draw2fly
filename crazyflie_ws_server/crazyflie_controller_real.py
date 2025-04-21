import time
import threading
import cflib.crtp
from cflib.crazyflie import Crazyflie

class CrazyflieController:
    def __init__(self):
        # Initialize CRTP communication drivers
        cflib.crtp.init_drivers()
        self.uri = "radio://0/80/2M"
        self.cf = Crazyflie()
        self.connected = False

        # Hover control flags
        self.hovering = False
        self.hover_thread = None

        # Register callbacks
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

    def _hover_loop(self, z=0.5):
        while self.hovering:
            self.cf.commander.send_hover_setpoint(0.0, 0.0, 0.0, z)
            time.sleep(0.05)

    def start_hover(self, z=0.5):
        if not self.hovering:
            self.hovering = True
            self.hover_thread = threading.Thread(target=self._hover_loop, args=(z,))
            self.hover_thread.start()
            print(f"🌀 Started persistent hover at {z:.2f} m")

    def stop_hover(self):
        if self.hovering:
            self.hovering = False
            if self.hover_thread:
                self.hover_thread.join()
                self.hover_thread = None
            self.cf.commander.send_stop_setpoint()
            print("🛑 Hovering stopped and motors halted")

    async def takeoff(self, height: float = 0.5, duration: float = 3.0):
        print(f"🚁 Taking off to {height:.2f} m")

        self.stop_hover()  # In case called twice

        self.cf.commander.send_hover_setpoint(0.0, 0.0, 0.0, 0.1)
        time.sleep(0.5)

        start_time = time.time()
        while time.time() - start_time < duration:
            self.cf.commander.send_hover_setpoint(0.0, 0.0, 0.0, height)
            time.sleep(0.05)

        self.start_hover(z=height)
        print(f"✅ Hovering at {height:.2f} m and waiting for future commands")

    async def land(self, duration: float = 3.0):
        print("🛬 Landing")
        self.stop_hover()

        steps = 20
        for i in range(steps, -1, -1):
            z = i * (0.5 / steps)
            self.cf.commander.send_hover_setpoint(0.0, 0.0, 0.0, z)
            time.sleep(duration / steps)

        self.cf.commander.send_stop_setpoint()
        print("🛑 Motors stopped")

    async def follow_waypoints(self, points):
        print(f"📍 Executing {len(points)} waypoints")
        self.stop_hover()

        for i, pt in enumerate(points):
            x = float(pt["x"])
            y = float(pt["y"])
            z = 0.5  # fixed height
            print(f"   ➤ Moving to ({x:.2f}, {y:.2f}, {z:.2f})")
            self.cf.commander.send_position_setpoint(x, y, z, 0.0)
            time.sleep(0.5)

        # After reaching final point, hold hover again
        self.start_hover(z=0.5)
        print("⏸️ Resumed hover after path")
