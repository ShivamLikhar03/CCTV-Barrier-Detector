from flask import Flask, render_template, Response, request, jsonify
import cv2
import numpy as np
import time
import os
import threading
from datetime import datetime

app = Flask(__name__)

# Global variables
camera = None
camera_url = None
connected = False
frame_buffer = None
obstruction_detected = False
obstruction_start_time = None
alarm_active = False
darkness_threshold = 25
alarm_duration = 20
is_jpg_mode = False
camera_thread = None
running = False

def log_event(event_type):
    """Log obstruction events to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("obstruction_log.txt", "a") as f:
        f.write(f"{timestamp} - {event_type}\n")

def is_frame_dark(frame, threshold=25):
    """
    Check if the frame is dark/obstructed.
    Returns True if average pixel value is below threshold.
    """
    if frame is None:
        return False
    avg_value = np.mean(frame)
    return avg_value < threshold

def camera_stream():
    global camera, frame_buffer, obstruction_detected, obstruction_start_time, alarm_active, running, is_jpg_mode
    
    running = True
    while running:
        try:
            if is_jpg_mode:
                # For shot.jpg method, we need to recreate the capture for each frame
                cap = cv2.VideoCapture(camera_url)
                success, frame = cap.read()
                cap.release()
            else:
                success, frame = camera.read()
                
            if not success:
                print("Failed to get frame")
                # Try to reconnect
                if not is_jpg_mode:
                    camera.release()
                    camera = cv2.VideoCapture(camera_url)
                time.sleep(1)
                continue
                
            # Check if frame is dark/obstructed
            if is_frame_dark(frame, darkness_threshold):
                # If obstruction just started
                if obstruction_start_time is None:
                    obstruction_start_time = time.time()
                    print("Obstruction detected! Monitoring...")
                    log_event("Obstruction detected")
                    obstruction_detected = True
                
                # Check if obstruction has lasted more than the specified duration
                elapsed_time = time.time() - obstruction_start_time
                
                # Display the elapsed time on the frame
                cv2.putText(frame, f"Obstruction: {elapsed_time:.1f}s", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                if elapsed_time >= alarm_duration and not alarm_active:
                    print(f"ALERT! Camera obstructed for {alarm_duration} seconds!")
                    log_event("Alarm triggered")
                    alarm_active = True
            else:
                # If no obstruction, reset timer and stop alarm
                if obstruction_start_time is not None:
                    print("Obstruction cleared")
                    log_event("Obstruction cleared")
                    obstruction_start_time = None
                    obstruction_detected = False
                
                if alarm_active:
                    alarm_active = False
            
            # Display status on the frame
            status = "OBSTRUCTED" if obstruction_detected else "NORMAL"
            color = (0, 0, 255) if status == "OBSTRUCTED" else (0, 255, 0)
            cv2.putText(frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Encode the frame for streaming
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_buffer = buffer.tobytes()
            
            # For jpg mode, add a delay
            if is_jpg_mode:
                time.sleep(0.1)  # Small delay to prevent overloading the server

        except Exception as e:
            print(f"Error in camera stream: {e}")
            time.sleep(1)
    
    if not is_jpg_mode and camera is not None:
        camera.release()
    print("Camera thread stopped")

def gen_frames():
    global frame_buffer
    while True:
        if frame_buffer is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
        else:
            # If no frame is available, send a blank frame
            blank_frame = np.zeros((480, 640, 3), np.uint8)
            _, buffer = cv2.imencode('.jpg', blank_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.033)  # ~30 FPS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/connect', methods=['POST'])
def connect_camera():
    global camera, camera_url, connected, is_jpg_mode, camera_thread, running, darkness_threshold, alarm_duration
    
    # Stop any existing camera thread
    if camera_thread and camera_thread.is_alive():
        running = False
        camera_thread.join(timeout=3)
    
    # Get camera URL from form
    ip = request.form.get('camera_ip', '192.168.1.6:8080')
    darkness_threshold = int(request.form.get('threshold', 25))
    alarm_duration = int(request.form.get('duration', 20))
    
    # Try different video URL formats
    video_urls = [
        f'http://{ip}/video',
        f'http://{ip}/videofeed',
        f'http://{ip}/shot.jpg'
    ]
    
    connected = False
    error_message = "Failed to connect to camera"
    
    for url in video_urls:
        print(f"Trying to connect to {url}")
        try:
            is_jpg_mode = url.endswith('shot.jpg')
            camera_url = url
            
            if is_jpg_mode:
                # For shot.jpg, we'll recreate the capture for each frame in the thread
                cap = cv2.VideoCapture(url)
                success = cap.isOpened()
                cap.release()
            else:
                camera = cv2.VideoCapture(url)
                success = camera.isOpened()
                
            if success:
                connected = True
                print(f"Successfully connected to {url}")
                
                # Start camera thread
                camera_thread = threading.Thread(target=camera_stream)
                camera_thread.daemon = True
                camera_thread.start()
                
                return jsonify({
                    'success': True,
                    'message': f"Connected to {url}",
                    'threshold': darkness_threshold,
                    'duration': alarm_duration
                })
        except Exception as e:
            error_message = f"Error connecting to {url}: {str(e)}"
            print(error_message)
    
    return jsonify({
        'success': False,
        'message': error_message
    })

@app.route('/status')
def get_status():
    global obstruction_detected, alarm_active, obstruction_start_time
    
    elapsed_time = 0
    if obstruction_detected and obstruction_start_time is not None:
        elapsed_time = time.time() - obstruction_start_time
    
    return jsonify({
        'connected': connected,
        'obstruction_detected': obstruction_detected,
        'alarm_active': alarm_active,
        'elapsed_time': elapsed_time,
        'threshold': darkness_threshold,
        'duration': alarm_duration
    })

@app.route('/logs')
def get_logs():
    logs = []
    try:
        with open("obstruction_log.txt", "r") as f:
            logs = [line.strip() for line in f.readlines()]
            logs.reverse()  # Most recent first
    except FileNotFoundError:
        pass
    
    return jsonify({
        'logs': logs[:50]  # Return only the last 50 logs
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True) 