from flask import Flask, render_template, request, send_from_directory
from picamera2 import Picamera2
import cv2
import numpy as np
import os
import time
import serial

app = Flask(__name__)

picam = Picamera2()
output_dir = "static/photos"
os.makedirs(output_dir, exist_ok=True)
photo_path = os.path.join(output_dir, "photo.jpg")
processed_path = os.path.join(output_dir, "processed_photo.jpg")

@app.route('/')
def index():
    return render_template('index.html', photo_exists=os.path.exists(processed_path))

@app.route('/shoot', methods=['POST'])
def shoot():
    time.sleep(5)  # Sleep for stabilization
    global photo_path, processed_path
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

    # Ensure the subject remains visible (no blank areas)
    background = np.zeros_like(image)  # Black background
    combined = cv2.add(foreground, background)

    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(combined, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges using Canny for more precise outlines
    edges = cv2.Canny(blurred, 50, 150)

    # Remove small dots/noise using morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    cleaned_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Remove internal details of hair (outline only)
    contours, _ = cv2.findContours(cleaned_edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) > 200:  # Threshold for hair
            cv2.drawContours(cleaned_edges, [contour], -1, 255, thickness=cv2.FILLED)

    # Dilate and erode for smooth, connected lines
    final_edges = cv2.dilate(cleaned_edges, kernel, iterations=1)
    final_edges = cv2.erode(final_edges, kernel, iterations=1)

    # Save the processed image
    cv2.imwrite(processed_path, final_edges)
    return render_template('index.html', photo_exists=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
