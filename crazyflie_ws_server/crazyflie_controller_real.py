import asyncio
import time
import cflib.crtp
from cflib.crazyflie import Crazyflie

class CrazyflieController:
    def __init__(self):
        cflib.crtp.init_drivers()
        self.uri = "radio://0/10/2M/E7E7E7E703"
        self.cf = Crazyflie()
        self.connected = False

        # Hovering control
        self.hovering = False
        self.hover_height = 0.5
        self.hover_task = None

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

    async def _hover_loop(self):
        try:
            while self.hovering:
                self.cf.commander.send_hover_setpoint(0.0, 0.0, 0.0, self.hover_height)
                await asyncio.sleep(0.05)
        except asyncio.CancelledError:
            print("⛔ Hover loop cancelled")

    async def start_hover(self, z=0.5):
        if not self.hovering:
            self.hovering = True
            self.hover_height = z
            self.hover_task = asyncio.create_task(self._hover_loop())
            print(f"🌀 Started hover at {z:.2f} m")

    async def stop_hover(self, halt_motors=False):
        if self.hovering:
            self.hovering = False
            if self.hover_task:
                self.hover_task.cancel()
                try:
                    await self.hover_task
                except asyncio.CancelledError:
                    pass
                self.hover_task = None
            if halt_motors:
                self.cf.commander.send_stop_setpoint()
                print("🛑 Hovering stopped and motors halted")
            else:
                print("🛑 Hovering loop stopped, drone maintains last setpoint")

    async def takeoff(self, height: float = 0.5, duration: float = 3.0):
        print(f"🚁 Taking off to {height:.2f} m")
        await self.stop_hover()

        self.hovering = True
        self.hover_height = 0.1
        self.hover_task = asyncio.create_task(self._hover_loop())

        steps = int(duration / 0.05)
        for i in range(steps):
            self.hover_height = 0.1 + (height - 0.1) * (i / steps)
            await asyncio.sleep(0.05)

        self.hover_height = height
        print(f"✅ Hovering at {height:.2f} m")

    async def land(self, duration: float = 3.0):
        print("🛬 Landing")
        if not self.hovering:
            await self.start_hover(z=0.5)

        steps = int(duration / 0.05)
        initial_height = self.hover_height

        for i in range(steps):
            self.hover_height = initial_height * (1 - i / steps)
            await asyncio.sleep(0.05)

        self.hover_height = 0.0
        await asyncio.sleep(0.1)
        await self.stop_hover(halt_motors=True)

    async def follow_waypoints(self, points, speed=0.5):
        print(f"📍 Executing {len(points)} waypoints")
        await self.stop_hover()

        dt = 0.05  # 20 Hz
        for i, pt in enumerate(points):
            x = float(pt["x"])
            y = float(pt["y"])
            z = 0.5
            print(f"   ➤ Moving to ({x:.2f}, {y:.2f}, {z:.2f})")

            steps = int(1.0 / dt)
            for j in range(steps):
                r = (j + 1) / steps
                self.cf.commander.send_position_setpoint(x * r, y * r, z, 0.0)
                await asyncio.sleep(dt)

            self.cf.commander.send_position_setpoint(x, y, z, 0.0)
            await asyncio.sleep(0.2)

        await self.start_hover(z=0.5)
        print("⏸️ Resumed hover after path")
