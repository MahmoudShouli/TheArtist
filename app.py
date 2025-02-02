from flask import Flask, render_template, request, send_from_directory, url_for, redirect
from picamera2 import Picamera2
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
import time
import serial
from gcode_operations import configure_grbl
from data import gcode_commands_blue, gcode_commands_red, gcode_retrieve_red, gcode_retrieve_blue
from data import gcode_array, gcode_A3_signature, gcode_A4_signature
app = Flask(__name__)

picam = Picamera2()


isPenFinished = False
isPaperFinished = False
isStartRetrieve = False
isDrawingDone = False
isWholeProcessFinished = False


gcode_path = './gcode/drawing.gcode'
a4sig_path = './gcode/a4sig.gcode'
a3sig_path = './gcode/a3sig.gcode'

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




def convert_gcodefile_to_array(file, arr):
    with open(file, 'r') as gcode_file:
        for line in gcode_file:
            cleaned_line = line.split(';')[0].strip() 
            if cleaned_line:  
                arr.append(cleaned_line)


@app.route('/')
def index():
    return render_template('index.html', photo_exists=os.path.exists(processed_path))


@app.route('/upload', methods=['POST'])
def upload_gcode():
    global gcode_path, a3sig_path, a4sig_path
    global gcode_array, gcode_A3_signature, gcode_A4_signature
    
    
    if 'gcode_file' not in request.files:
        return "No file part", 400
    file = request.files['gcode_file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.gcode'):
        file.save(gcode_path)  
        print("G-code file uploaded and saved as 'drawing.gcode'")
        
        convert_gcodefile_to_array(gcode_path, gcode_array)
        gcode_array.append('G00 Z0')
        gcode_array.append('G00 X0 Y0')
        convert_gcodefile_to_array(a3sig_path, gcode_A3_signature)
        convert_gcodefile_to_array(a4sig_path, gcode_A4_signature)

        return redirect(url_for('index'))
    else:
        return "Invalid file format. Please upload a .gcode file.", 400


@app.route('/start', methods=['POST'])
def start():
        
    global isPenFinished, isPaperFinished, isStartRetrieve, isDrawingDone, isWholeProcessFinished
   
    page_size = request.form.get('pageSize')  # 'A4' or 'A3'
    pen_color = request.form.get('penColor')  # 'Blue' or 'Red'

    
    if  pen_color == 'Blue' :
        serMega.write('PB\n'.encode())
        isPenFinished = configure_grbl(uno, gcode_commands_blue, True)
        

    elif pen_color == 'Red':
        serMega.write('PB\n'.encode())
        isPenFinished = configure_grbl(uno, gcode_commands_red, True)
    

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
        serMega.write('DRAWING\n'.encode())
        isDrawingDone = configure_grbl(uno, gcode_array, False)


    if isDrawingDone:
        serMega.write('SIGN\n'.encode())
        if page_size == 'A3':
            isStartRetrieve = configure_grbl(uno, gcode_A3_signature, False)
        elif page_size == 'A4':
            isStartRetrieve = configure_grbl(uno, gcode_A4_signature, False)

    if isStartRetrieve:
        serMega.write('RET\n'.encode())
        if pen_color == 'Blue':
            isWholeProcessFinished = configure_grbl(uno, gcode_retrieve_blue, True)
        elif pen_color == 'Red':
            isWholeProcessFinished = configure_grbl(uno, gcode_retrieve_red, True)

    if isWholeProcessFinished:
        serMega.write('DONE\n'.encode()) 
        print("Sent to Arduino: DONE")
    

    return redirect(url_for('index'))  


from flask import Flask, render_template
import cv2
import numpy as np

app = Flask(__name__)

photo_path = "captured.jpg"
processed_path = "processed.jpg"

@app.route('/shoot', methods=['POST'])
def shoot():
    global photo_path, processed_path

    # Capture photo
    picam.start()
    picam.capture_file(photo_path)
    picam.stop()

    # Load the image
    image = cv2.imread(photo_path)

    # Convert to HSV for masking
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define green color range for masking
    lower_green = np.array([30, 30, 30])
    upper_green = np.array([90, 255, 255])

    # Create a mask for green color
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask_inv = cv2.bitwise_not(mask)

    # Replace green background with white
    white_background = np.full_like(image, 255, dtype=np.uint8)
    result = np.where(mask[:, :, None].astype(bool), white_background, image)

    # Apply a small sharpening filter
    sharpening_kernel = np.array([[0, -0.3, 0], [-0.3, 2, -0.3], [0, -0.3, 0]])
    sharpened_image = cv2.filter2D(result, -1, sharpening_kernel)

    # Enhance brightness
    brightness_factor = 30  # Adjust brightness level
    brightened_image = cv2.add(sharpened_image, np.array([brightness_factor], dtype=np.uint8))

    # Save the processed image
    cv2.imwrite(processed_path, brightened_image)

    return render_template('index.html', photo_exists=True)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)