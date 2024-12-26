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
    time.sleep(5)  # Stabilization delay
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

    # Invert the mask to focus on the subject
    mask_inv = cv2.bitwise_not(mask)

    # Apply the mask to retain only the subject
    foreground = cv2.bitwise_and(image, image, mask=mask_inv)

    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply sharpening to enhance edges
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(blurred, -1, sharpen_kernel)

    # Apply adaptive thresholding for edge detection
    edges = cv2.adaptiveThreshold(
        sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Remove noise and preserve facial features
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    clean_face = np.zeros_like(edges)

    for contour in contours:
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)

        # Keep contours within a reasonable size range
        if 500 < area < 5000:  # Adjusted size range for facial features
            cv2.drawContours(clean_face, [contour], -1, 255, thickness=1)

    # Final cleanup: Remove stray dots using morphological operations
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    clean_face = cv2.morphologyEx(clean_face, cv2.MORPH_OPEN, kernel, iterations=1)

    # Save the final processed image
    cv2.imwrite(processed_path, clean_face)
    return render_template('index.html', photo_exists=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
