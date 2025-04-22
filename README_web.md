# CCTV Obstruction Monitor Web Application

This web application allows you to monitor CCTV cameras for obstructions or darkness and receive alerts when an obstruction is detected for a specified duration.

## Features

- Connect to IP cameras by providing IP address and port
- Real-time video streaming in the browser
- Detects camera obstructions/darkness based on configurable threshold
- Visual and audio alerts when obstruction persists for a specified duration
- Event logging with timestamp
- Mobile-responsive design

## Requirements

- Python 3.6 or later
- OpenCV
- Flask
- NumPy
- PyGame (for audio processing)

## Installation

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python app.py
   ```
2. Open your web browser and navigate to:
   ```
   http://localhost:5000
   ```
3. Enter the IP address and port of your IP camera (e.g., 192.168.1.6:8080)
4. Configure the darkness threshold and alarm duration
5. Click "Connect" to start monitoring

## Compatible Cameras

This application is designed to work with:

1. IP Webcam mobile apps that provide HTTP streams
2. Most network cameras with HTTP streaming capabilities
3. Cameras with RTSP streams (may require additional configuration)

The application will attempt to connect to the camera using several common URL formats:
- http://IP:PORT/video
- http://IP:PORT/videofeed
- http://IP:PORT/shot.jpg

## Customization

- Adjust the darkness threshold (0-255) to match your lighting conditions
- Set the alarm duration to control how long an obstruction must persist before triggering an alarm

## Troubleshooting

- If the camera doesn't connect, ensure the IP address and port are correct
- Check that your camera is accessible from the device running the application
- Verify that your camera provides an HTTP stream in a compatible format 