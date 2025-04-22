import cv2
import numpy as np
import time
import pygame
import argparse
from datetime import datetime

def initialize_pygame():
    """Initialize pygame for playing alarm sound."""
    pygame.mixer.init()
    pygame.mixer.music.load('alert.wav')

def is_frame_dark(frame, threshold=25):
    """
    Check if the frame is dark/obstructed.
    Returns True if average pixel value is below threshold.
    """
    avg_value = np.mean(frame)
    return avg_value < threshold

def log_event(event_type):
    """Log obstruction events to a file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("obstruction_log.txt", "a") as f:
        f.write(f"{timestamp} - {event_type}\n")

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='CCTV Obstruction Detection')
    parser.add_argument('--ip', type=str, default='192.168.1.6:8080',
                        help='IP address and port of IP Webcam app (default: 192.168.1.6:8080)')
    parser.add_argument('--threshold', type=int, default=25,
                        help='Darkness threshold (0-255, default: 25)')
    parser.add_argument('--duration', type=int, default=20,
                        help='Duration in seconds before alarm (default: 20)')
    args = parser.parse_args()

    # Initialize pygame for alarm sound
    initialize_pygame()

    # Try different video URL formats commonly used by IP Webcam app
    video_urls = [
        f'http://{args.ip}/video',
        f'http://{args.ip}/videofeed',
        f'http://{args.ip}/shot.jpg'
    ]
    
    cap = None
    connected_url = None
    
    for url in video_urls:
        print(f"Trying to connect to {url}")
        cap = cv2.VideoCapture(url)
        if cap.isOpened():
            connected_url = url
            print(f"Successfully connected to {connected_url}")
            break
        else:
            print(f"Failed to connect to {url}")
    
    if not cap or not cap.isOpened():
        print(f"Error: Could not connect to any camera stream at {args.ip}")
        return

    print(f"Connected to camera at {connected_url}")
    print(f"Monitoring for obstructions (darkness threshold: {args.threshold})")
    print(f"Alarm will trigger after {args.duration} seconds of obstruction")

    obstruction_start_time = None
    alarm_active = False

    # For the shot.jpg method, we need to handle it differently
    is_jpg_mode = connected_url.endswith('shot.jpg')

    try:
        while True:
            if is_jpg_mode:
                # For shot.jpg method, we need to recreate the capture for each frame
                cap = cv2.VideoCapture(connected_url)
            
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame")
                time.sleep(1)
                # Try to reconnect
                cap = cv2.VideoCapture(connected_url)
                continue

            # Check if frame is dark/obstructed
            if is_frame_dark(frame, args.threshold):
                # If obstruction just started
                if obstruction_start_time is None:
                    obstruction_start_time = time.time()
                    print("Obstruction detected! Monitoring...")
                    log_event("Obstruction detected")
                
                # Check if obstruction has lasted more than the specified duration
                elapsed_time = time.time() - obstruction_start_time
                
                # Display the elapsed time on the frame
                cv2.putText(frame, f"Obstruction: {elapsed_time:.1f}s", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                
                if elapsed_time >= args.duration and not alarm_active:
                    print(f"ALERT! Camera obstructed for {args.duration} seconds!")
                    log_event("Alarm triggered")
                    pygame.mixer.music.play(-1)  # Play alarm sound on loop
                    alarm_active = True
            else:
                # If no obstruction, reset timer and stop alarm
                if obstruction_start_time is not None:
                    print("Obstruction cleared")
                    log_event("Obstruction cleared")
                    obstruction_start_time = None
                
                if alarm_active:
                    pygame.mixer.music.stop()
                    alarm_active = False
            
            # Display status on the frame
            status = "OBSTRUCTED" if obstruction_start_time else "NORMAL"
            color = (0, 0, 255) if status == "OBSTRUCTED" else (0, 255, 0)
            cv2.putText(frame, status, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            
            # Display the frame
            cv2.imshow('CCTV Monitor', frame)
            
            # Exit on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
            # If using the shot.jpg method, we need to release the capture after each frame
            if is_jpg_mode:
                cap.release()
                time.sleep(0.1)  # Small delay to prevent overloading the server
                
    except KeyboardInterrupt:
        print("Monitoring stopped by user")
    finally:
        if alarm_active:
            pygame.mixer.music.stop()
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 