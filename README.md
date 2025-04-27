# Draw2Fly: Intuitive Path Drawing for Autonomous Drone Navigation

**Draw2Fly** is a research prototype that enables users to control a Crazyflie 2.0 nano quadcopter by simply drawing a flight path on a mobile device. The system translates these drawings into precise drone movements, allowing for intuitive and accessible drone navigation without the need for manual piloting or complex programming.

## System Architecture

- **Mobile App**: Users draw flight paths on a touch interface. The app processes these inputs into waypoints and sends them via WebSocket to the server.
- **Server**: Receives waypoint data and control commands from the mobile app. It utilizes the `cflib` Python library to communicate with the Crazyflie 2.0 drone, sending appropriate flight commands.
- **Crazyflie 2.0 Drone**: Executes the received commands, following the specified waypoints with the help of onboard sensors for stable flight.

## Repository Structure

```
draw2fly/
├── crazyflie_ws_server/
│   ├── main.py
│   └── crazyflie_controller_real.py
│   └── crazyflie_controller.py
├── README.md
```

- `crazyflie_ws_server/`: Contains the server-side code responsible for handling WebSocket connections and interfacing with the Crazyflie drone.
  - `main.py`: Initializes the WebSocket server and manages incoming connections and messages.
  - `crazyflie_controller.py`: Defines the mock `CrazyflieController` class for connection testing.
  - `crazyflie_controller_real.py`: Defines the `CrazyflieController` class, which handles drone commands such as takeoff, landing, and waypoint navigation.

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- [Crazyflie 2.0](https://www.bitcraze.io/products/crazyflie-2/) nano quadcopter
- [Crazyradio PA](https://www.bitcraze.io/products/crazyradio-pa/) USB dongle
- [cflib](https://github.com/bitcraze/crazyflie-lib-python) Python library
- Mobile device with the Draw2Fly app installed

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/RuiyangWangW/draw2fly.git
cd draw2fly/crazyflie_ws_server
```

2. **Create a virtual environment and activate it:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install the required Python packages:**

```bash
pip install -r requirements.txt
```

4. **Connect the Crazyradio PA dongle to your computer.**

5. **Run the server:**

```bash
python main.py
```

The server will start and listen for incoming WebSocket connections from the mobile app.

### Mobile App Setup

*Note: The mobile app code is not included in this repository. Ensure that you have the Draw2Fly mobile app installed on your device.*

1. Connect the mobile device to the same network as the server.
2. Open the Draw2Fly app and enter the server's IP address (e.g., `10.0.2.2`) to establish a connection.
3. Draw a flight path on the app's interface and send it to the server.
4. Use the app's controls to initiate takeoff, landing, or emergency stop as needed.

## 🧪 Features

- **Intuitive Path Drawing**: Users can draw complex flight paths directly on their mobile devices.
- **Real-Time Communication**: The system uses WebSocket for low-latency communication between the mobile app and the server.
- **Smooth Waypoint Navigation**: The server interpolates between waypoints to ensure smooth drone movements.
- **Safety Measures**: Includes emergency stop functionality and maintains stable hover when idle.

## 🧰 Troubleshooting

- **Connection Issues**: Ensure that the Crazyradio PA dongle is properly connected and recognized by your system. Verify that the server and mobile device are on the same network.
- **Drone Drift**: If the drone drifts during flight, check the optical flow sensor for dust or damage. Replacing the sensor or recalibrating may be necessary.
- **Waypoint Execution Errors**: Ensure that the waypoints sent from the mobile app are within the drone's operational range and that the server is correctly processing them.


## 📬 Contact

For questions or feedback, please contact [Ruiyang Wang](ruiyang.wang@duke.edu).

   
