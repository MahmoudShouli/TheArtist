from flask import Flask, render_template, request, send_from_directory
from picamera2 import Picamera2
import cv2
import numpy as np
import os
import time

app = Flask(__name__)

# Initialize the camera
picam = Picamera2()

# Directory for storing photos and generated files
output_dir = "static/photos"
os.makedirs(output_dir, exist_ok=True)
photo_path = os.path.join(output_dir, "photo.jpg")
processed_path = os.path.join(output_dir, "processed_photo.jpg")
gcode_path = os.path.join(output_dir, "output.gcode")

# CNC plotter-specific parameters
PEN_UP = 0  # Z position for pen up
PEN_DOWN = 3.1  # Z position for pen down
FEED_RATE_DRAW = 1800.0  # Feed rate for drawing
FEED_RATE_MOVE = 2400.0  # Feed rate for fast moves
PAPER_WIDTH = 210  # Width of A4 paper in mm
PAPER_HEIGHT = 297  # Height of A4 paper in mm

@app.route('/')
def index():
    return render_template('index.html', photo_exists=os.path.exists(processed_path))

@app.route('/shoot', methods=['POST'])
def shoot():
    time.sleep(5)  # Allow some time for setup
    global photo_path, processed_path

    # Capture the image
    picam.start()
    picam.capture_file(photo_path)
    picam.stop()

    # Read the captured image
    image = cv2.imread(photo_path)

    # Convert to HSV for better background masking
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 55, 55])  # Adjust for green background
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Invert the mask to focus on the subject (non-green parts)
    mask_inv = cv2.bitwise_not(mask)

    # Apply the mask to retain only the subject
    foreground = cv2.bitwise_and(image, image, mask=mask_inv)

    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)

    # Enhance contrast using CLAHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Apply Gaussian blur for slight smoothing
    blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)

    # Apply refined Canny edge detection
    edges = cv2.Canny(blurred, threshold1=30, threshold2=100)

    # Use morphological operations to clean up edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # Invert the colors for black features on a white background
    final_output = cv2.bitwise_not(cleaned_edges)

    # Save the processed image
    cv2.imwrite(processed_path, final_output)












    return render_template('index.html', photo_exists=True)

def generate_gcode_from_image(image_path, gcode_path):
    # Load the processed image
    edges = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Find contours in the edge-detected image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Open the G-code file for writing
    with open(gcode_path, "w") as gcode_file:
        gcode_file.write("G21 ; Set units to mm\n")
        gcode_file.write("G90 ; Absolute positioning\n")
        gcode_file.write(f"G00 Z{PEN_UP} ; Pen up\n")

        # Map image coordinates to plotter coordinates
        height, width = edges.shape
        scale_x = PAPER_WIDTH / width
        scale_y = PAPER_HEIGHT / height

        for contour in contours:
            if len(contour) < 2:
                continue  # Skip small or invalid contours

            # Move to the starting point of the contour
            x, y = contour[0][0]
            x_mm = x * scale_x
            y_mm = PAPER_HEIGHT - (y * scale_y)  # Invert y-axis for CNC coordinate system
            gcode_file.write(f"G00 X{x_mm:.2f} Y{y_mm:.2f} F{FEED_RATE_MOVE}\n")
            gcode_file.write(f"G00 Z{PEN_DOWN} ; Pen down\n")

            # Draw the contour
            for point in contour:
                x, y = point[0]
                x_mm = x * scale_x
                y_mm = PAPER_HEIGHT - (y * scale_y)
                gcode_file.write(f"G01 X{x_mm:.2f} Y{y_mm:.2f} F{FEED_RATE_DRAW}\n")

            # Lift the pen after completing the contour
            gcode_file.write(f"G00 Z{PEN_UP} ; Pen up\n")

        gcode_file.write("M30 ; Program end\n")

@app.route('/generate_gcode', methods=['POST'])
def generate_gcode():
    global processed_path, gcode_path
    generate_gcode_from_image(processed_path, gcode_path)
    return send_from_directory(output_dir, "output.gcode", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
