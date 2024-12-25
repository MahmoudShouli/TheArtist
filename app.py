from flask import Flask, render_template, request, send_from_directory
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

    # Convert to HSV for background masking
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 55, 55])  # Adjust for green background
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Invert the mask to focus on the subject
    mask_inv = cv2.bitwise_not(mask)

    # Apply the mask to retain only the subject
    foreground = cv2.bitwise_and(image, image, mask=mask_inv)

    # Convert to grayscale
    gray = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)

    # Reduce noise with Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Edge detection using adaptive thresholding
    edges = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Remove noise and small contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    simplified_edges = np.zeros_like(edges)
    for contour in contours:
        if cv2.contourArea(contour) > 200:  # Threshold for significant contours
            # Simplify the contour to reduce noise
            epsilon = 0.01 * cv2.arcLength(contour, True)
            simplified_contour = cv2.approxPolyDP(contour, epsilon, True)
            cv2.drawContours(simplified_edges, [simplified_contour], -1, 255, thickness=1)

    # Morphological operations to smooth and connect lines
    kernel = np.ones((3, 3), np.uint8)
    smoothed_edges = cv2.morphologyEx(simplified_edges, cv2.MORPH_CLOSE, kernel, iterations=2)

    # Save the final processed image
    cv2.imwrite(processed_path, smoothed_edges)
    return render_template('index.html', photo_exists=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
