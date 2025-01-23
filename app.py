from flask import Flask, render_template, request, send_from_directory, url_for, redirect
from picamera2 import Picamera2
import cv2
import numpy as np
import os
import time
import serial
from sendGcode import configure_grbl
from data import gcode_commands_blue, gcode_commands_black, gcode_drawing
app = Flask(__name__)

#picam = Picamera2()

isPenFinished = False
isPaperFinished = False

output_dir = "static/photos"
os.makedirs(output_dir, exist_ok=True)
photo_path = os.path.join(output_dir, "photo.jpg")
processed_path = os.path.join(output_dir, "processed_photo.jpg")

mega = '/dev/ttyACM1'  
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
    global isPaperFinished

    page_size = request.form.get('pageSize')  # 'A4' or 'A3'
    pen_color = request.form.get('penColor')  # 'Blue' or 'Black'

    if  pen_color == 'Blue' :
        isPenFinished = configure_grbl(uno, gcode_commands_blue, True)
        

    elif pen_color == 'Black':
        isPenFinished = configure_grbl(uno, gcode_commands_black, True)
    


    if  page_size == 'A3' and isPenFinished:
        if serMega is None:
            return "Error: Mega not connected."
        try:
            serMega.write('A3\n'.encode())  
            print("Sent to Arduino: A3")  
            while True:
                if serMega.in_waiting > 0:
                    data = serMega.readline().decode('utf-8').rstrip()
                    if data == 'Paper detected, stopping stepper motor.':
                        isPaperFinished = True
                        break
        except Exception as e:
            print(f"Error: {e}")
    
    elif page_size == 'A4' and isPenFinished: 
        if serMega is None:
            return "Error: Mega not connected."
        try:
            serMega.write('A4\n'.encode())  
            print("Sent to Arduino: A4")  
            # while True:
            #     if serMega.in_waiting > 0:
            #         data = serMega.readline().decode('utf-8').rstrip()
            #         if data == 'Paper detected, stopping stepper motor.':
            #             isPaperFinished = True
            #             break
            
        except Exception as e:
            print(f"Error: {e}")

    if isPaperFinished:
        configure_grbl(uno, gcode_drawing, False)
    

    return redirect(url_for('index'))  


@app.route('/shoot', methods=['POST'])
def shoot():
    global photo_path, processed_path
    time.sleep(3)
    picam.start()
    picam.capture_file(photo_path)
    picam.stop()

    
    image = cv2.imread(photo_path)

    
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 55, 55])  
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

    # Apply sharpening to enhance edges
    sharpen_kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharpened = cv2.filter2D(blurred, -1, sharpen_kernel)

    # Apply adaptive thresholding for edge detection
    edges = cv2.adaptiveThreshold(
        sharpened, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # Remove small dots/noise using contour filtering
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        if cv2.contourArea(contour) < 150:  # Increased area threshold
            cv2.drawContours(edges, [contour], -1, (0, 0, 0), -1)

    # Apply median blur to further clean noise
    cleaned_edges = cv2.medianBlur(edges, 5)

    # Save the cleaned image
    cv2.imwrite(processed_path, cleaned_edges)
    return render_template('index.html', photo_exists=True)






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
