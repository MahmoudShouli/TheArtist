from flask import Flask, render_template, request
from picamera2 import Picamera2
import cv2
import numpy as np
import os
import time

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

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply adaptive thresholding for edge detection
    edges = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Remove noise and small contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    clean_edges = np.zeros_like(edges)
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Keep only significant contours
            cv2.drawContours(clean_edges, [contour], -1, 255, thickness=1)

    # Morphological operations to smooth and connect lines
    kernel = np.ones((3, 3), np.uint8)
    smoothed_edges = cv2.morphologyEx(clean_edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    # Additional cleaning: ensure no filled sections
    contours, _ = cv2.findContours(smoothed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    final_edges = np.zeros_like(smoothed_edges)
    for contour in contours:
        cv2.drawContours(final_edges, [contour], -1, 255, thickness=1)

    # Save the final processed image
    cv2.imwrite(processed_path, final_edges)
    return render_template('index.html', photo_exists=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
