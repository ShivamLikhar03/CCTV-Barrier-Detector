# CCTV Obstruction Detection System

This system monitors a camera feed from the IP Webcam app and detects if the camera is obstructed (covered or in darkness) for more than a specified duration, then triggers an alarm.

## Requirements

- Python 3.x
- OpenCV
- NumPy
- Pygame
- IP Webcam app installed on your smartphone

## Installation

1. Install the required Python packages:

```bash
pip install opencv-python numpy pygame
```

2. Install the "IP Webcam" app on your Android smartphone from the Google Play Store.

## Setup

1. Open the IP Webcam app on your smartphone.
2. Start the server by tapping "Start server" in the app.
3. Note the IP address and port displayed at the bottom of the screen (e.g., http://192.168.1.100:8080).

## Usage

Run the script with the IP address and port of your IP Webcam app:

```bash
python cctv_monitor.py --ip 192.168.1.100:8080
```

### Optional Arguments

- `--threshold`: Darkness threshold (0-255, default: 25). Lower values detect only very dark obstructions.
- `--duration`: Duration in seconds before the alarm is triggered (default: 20).

Example:

```bash
python cctv_monitor.py --ip 192.168.1.100:8080 --threshold 30 --duration 15
```

## Features

- Detects when the camera is obstructed or in darkness
- Triggers an alarm sound after the specified duration of obstruction
- Logs all obstruction events with timestamps
- Visual display showing camera status and obstruction duration
- Automatic reconnection if the camera feed is lost

## Troubleshooting

- If the script cannot connect to the camera, verify that:
  - Your computer and smartphone are on the same WiFi network
  - The IP address and port are correct
  - The IP Webcam server is running on your phone
  - No firewall is blocking the connection

## Logs

Obstruction events are logged to `obstruction_log.txt` with timestamps. 

<img width="1469" alt="image" src="https://github.com/user-attachments/assets/98734e86-8394-45b0-ac29-6bdff4814fe3" />
