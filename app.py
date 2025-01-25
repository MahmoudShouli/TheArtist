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

picam = Picamera2()

uploaded_gcode_array = []
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


@app.route('/upload', methods=['POST'])
def upload_gcode():
    global uploaded_gcode_array

    if 'gcode_file' not in request.files:
        return "No file part", 400
    file = request.files['gcode_file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.gcode'):
        gcode_path = 'drawing.gcode'
        file.save(gcode_path)  # Save the file as 'drawing.gcode'
        print("G-code file uploaded and saved as 'drawing.gcode'")

        # Read the G-code file into an array
        
        with open(gcode_path, 'r') as gcode_file:
            for line in gcode_file:
                cleaned_line = line.strip()
                if cleaned_line:
                    uploaded_gcode_array.append(cleaned_line)
        
        print("Uploaded G-code array:", uploaded_gcode_array)

        return redirect(url_for('index'))
    else:
        return "Invalid file format. Please upload a .gcode file.", 400


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
            while True:
                if serMega.in_waiting > 0:
                    data = serMega.readline().decode('utf-8').rstrip()
                    if data == 'Paper detected, stopping stepper motor.':
                        isPaperFinished = True
                        break
            
        except Exception as e:
            print(f"Error: {e}")

    if isPaperFinished:
        configure_grbl(uno, uploaded_gcode_array, False)
    

    return redirect(url_for('index'))  


@app.route('/shoot', methods=['POST'])
def shoot():
    global photo_path, processed_path
    picam.start()
    picam.capture_file(photo_path)
    picam.stop()

    # Load the captured image
    image = cv2.imread(photo_path)

    # Convert the image to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range for green color and create a mask
    lower_green = np.array([35, 55, 55])
    upper_green = np.array([85, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Invert the mask to isolate non-green parts of the image
    mask_inv = cv2.bitwise_not(mask)

    # Apply the mask to remove the green background and green box
    foreground = cv2.bitwise_and(image, image, mask=mask_inv)

    # Convert to grayscale for edge detection
    gray = cv2.cvtColor(foreground, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to smooth the edges
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges using Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Find contours of the edges
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a blank image for drawing outlines
    outlines = np.zeros_like(edges)

    # Draw the contours on the blank image
    cv2.drawContours(outlines, contours, -1, (255), thickness=2)

    # Save the final image with only the outlines
    cv2.imwrite(processed_path, outlines)

    return render_template('index.html', photo_exists=True)







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
