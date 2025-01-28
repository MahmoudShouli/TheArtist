from flask import Flask, render_template, request, send_from_directory, url_for, redirect
from picamera2 import Picamera2
import cv2
import numpy as np
import paramiko
import os
import time
import serial
from gcode_operations import configure_grbl
from data import gcode_commands_blue, gcode_commands_red
app = Flask(__name__)

#picam = Picamera2()

gcode_array = [
    "G10 L20 P1 X0 Y0 Z0"
]
isPenFinished = False
isPaperFinished = False


gcode_path = 'drawing.gcode'

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



def transfer_file(local_path, remote_path, host, username, password):
    """
    Transfer a file from Raspberry Pi to Windows using SFTP.
    :param local_path: Path to the file on Raspberry Pi
    :param remote_path: Path to the folder on Windows
    :param host: Windows IP address
    :param username: Windows username
    :param password: Windows passwordgit
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password)
    sftp = ssh.open_sftp()
    sftp.put(local_path, remote_path)
    sftp.close()
    ssh.close()
    print(f"File {local_path} transferred to {remote_path}")



def convert_gcodefile_to_array(file):
    global gcode_array
    gcode_array = []  
    with open(file, 'r') as gcode_file:
        for line in gcode_file:
            cleaned_line = line.split(';')[0].strip() 
            if cleaned_line:  
                gcode_array.append(cleaned_line)


@app.route('/')
def index():
    return render_template('index.html', photo_exists=os.path.exists(processed_path))


@app.route('/upload', methods=['POST'])
def upload_gcode():
    global gcode_path
    global isUpload
    
    
    if 'gcode_file' not in request.files:
        return "No file part", 400
    file = request.files['gcode_file']
    if file.filename == '':
        return "No selected file", 400
    if file and file.filename.endswith('.gcode'):
        file.save(gcode_path)  
        print("G-code file uploaded and saved as 'drawing.gcode'")
        
        convert_gcodefile_to_array(gcode_path)

        return redirect(url_for('index'))
    else:
        return "Invalid file format. Please upload a .gcode file.", 400


@app.route('/start', methods=['POST'])
def start():
        
    global gcode_path
    global isPenFinished
    global isPaperFinished

    page_size = request.form.get('pageSize')  # 'A4' or 'A3'
    pen_color = request.form.get('penColor')  # 'Blue' or 'Red'

    
    if  pen_color == 'Blue' :
        isPenFinished = configure_grbl(uno, gcode_commands_blue, True)
        

    elif pen_color == 'Red':
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
        configure_grbl(uno, gcode_array, False)
    

    return redirect(url_for('index'))  


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
    lower_green = np.array([35, 55, 55])
    upper_green = np.array([85, 255, 255])

    # Create a mask for green color
    mask = cv2.inRange(hsv, lower_green, upper_green)
    mask_inv = cv2.bitwise_not(mask)

    # Remove the green background
    result = cv2.bitwise_and(image, image, mask=mask_inv)

    # Convert to LAB color space for better luminance adjustments
    lab = cv2.cvtColor(result, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    # Apply CLAHE to enhance luminance
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    l = clahe.apply(l)

    # Merge the LAB channels back
    enhanced_lab = cv2.merge((l, a, b))
    enhanced_image = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # Additional sharpening filter
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])  # Sharpening kernel
    sharpened_image = cv2.filter2D(enhanced_image, -1, kernel)

    # Increase contrast and brightness (values can be adjusted)
    alpha = 1.5  # Contrast control (1.0 = no change, >1.0 = more contrast)
    beta = 15    # Brightness control (0 = no change, >0 = brighter)
    bright_contrast_image = cv2.convertScaleAbs(sharpened_image, alpha=alpha, beta=beta)

    # Save the processed image
    cv2.imwrite(processed_path, bright_contrast_image)

    # Uncomment to transfer files (if needed):
    # transfer_file(photo_path, "C:/humans/photos", "172.23.2.135", "CARVA", "123321")
    # transfer_file(processed_path, "C:/humans/processed", "172.23.2.135", "CARVA", "123321")

    return render_template('index.html', photo_exists=True)












if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)