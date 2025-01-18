from flask import Flask, render_template, request, send_from_directory, url_for, redirect
from picamera2 import Picamera2
import cv2
import numpy as np
import os
import time
import serial
from sendGcode import configure_grbl

app = Flask(__name__)


# Initialize the camera
picam = Picamera2()

# Array of G-code commands to send
gcode_commands_black = [
    "G10 L20 P1 X0 Y0 Z0",  # Set current position as origin
    "G90",
    "M3 S150",                 
    "G00 Y39",              # Move to Y39
    "G00 X300",             # Move to X300
    "G00 Z4.5",             # Move to Z4.5
    "G00 X308",             # Move to X308
    "M3 S0",                # Turn spindle off
    "G00 Z0",               # Move Z to 0
    "G00 X0 Y0",
    "M3 S150"           # Move back to origin
]

    # Array of G-code commands to send
gcode_commands_blue = [
    "G10 L20 P1 X0 Y0 Z0",  # Set current position as origin
    "G90",                  # Set absolute positioning
    "M3 S150", 
    "G00 Y68",              # Move to Y39
    "G00 X300",             # Move to X300
    "G00 Z4.5",             # Move to Z4.5
    "G00 X308",             # Move to X308
    "M3 S0",                # Turn spindle off
    "G00 Z0",               # Move Z to 0
    "G00 X0 Y0",
    "M3 S150"           # Move back to origin
]

isPenFinished = False

# Directory for storing photos and generated files
output_dir = "static/photos"
os.makedirs(output_dir, exist_ok=True)
photo_path = os.path.join(output_dir, "photo.jpg")
processed_path = os.path.join(output_dir, "processed_photo.jpg")


# Serial port configuration
mega = '/dev/ttyACM1'  # Adjust based on your setup
uno = '/dev/ttyACM0'

try:
    serMega = serial.Serial(mega, 9600, timeout=1)
    print(f"Connected to Arduino on {mega}")
except Exception as e:
    print(f"Error: {e}")
    serMega = None

@app.route('/')
def index():
    return render_template('index.html', photo_exists=os.path.exists(processed_path))

@app.route('/start', methods=['POST'])
def start():

    global isPenFinished
    # Retrieve the selected options from the form
    page_size = request.form.get('pageSize')  # 'A4' or 'A3'
    pen_color = request.form.get('penColor')  # 'Blue' or 'Black'

    if  pen_color == 'Blue' :
        isPenFinished = configure_grbl(uno, gcode_commands_blue)
        

    elif pen_color == 'Black':
        isPenFinished = configure_grbl(uno, gcode_commands_black)
    


    if  page_size == 'A3' and isPenFinished:
        if serMega is None:
            return "Error: Mega not connected."
        try:
            serMega.write('A3\n'.encode())  # Send text to Mega
            print("Sent to Arduino: A3")  # Debug log
        except Exception as e:
            print(f"Error: {e}")
    
    elif page_size == 'A4' and isPenFinished: 
        if serMega is None:
            return "Error: Mega not connected."
        try:
            serMega.write('A4\n'.encode())  # Send text to Mega
            print("Sent to Arduino: A4")  # Debug log
        except Exception as e:
            print(f"Error: {e}")
    

    return redirect(url_for('index'))  # Redirect back to the main page


@app.route('/shoot', methods=['POST'])
def shoot():
    global photo_path, processed_path
    time.sleep(3)
    picam.start()
    picam.capture_file(photo_path)
    picam.stop()

    # Read the captured image
    image = cv2.imread(photo_path)

    # Convert to HSV for better background masking
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([30, 40, 40])  # Loosened green background range
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Invert the mask to focus on the subject (non-green parts)
    mask_inv = cv2.bitwise_not(mask)

    # Apply the mask to retain only the subject
    foreground = cv2.bitwise_and(image, image, mask=mask_inv)

    # Ensure the subject remains visible (no blank areas)
    background = np.zeros_like(image)  # Black background
    combined = cv2.add(foreground, background)

    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(combined, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Canny edge detection for better line control
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

    # Apply morphological closing to connect broken lines
    kernel = np.ones((5, 5), np.uint8)  # Larger kernel for stronger closing
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Apply median blur to further clean noise
    cleaned_edges = cv2.medianBlur(closed, 5)

    # Save the cleaned image
    cv2.imwrite(processed_path, cleaned_edges)
    return render_template('index.html', photo_exists=True)





if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
