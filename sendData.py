from flask import Flask, request, render_template, redirect, url_for
import serial

# Flask app
app = Flask(__name__)

# Serial port configuration
arduino_port = '/dev/ttyACM0'  # Adjust based on your setup
baud_rate = 9600
try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
except Exception as e:
    print(f"Error: {e}")
    ser = None

@app.route('/')
def index():
    return render_template('simple.html')  # Load the HTML form

@app.route('/A3', methods=['POST'])
def runA3():
    if ser is None:
        return "Error: Arduino not connected."
    try:
        ser.write('A3\n'.encode())  # Send text to Arduino
        print("Sent to Arduino: A3")  # Debug log
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for('index'))  # Redirect back to the main page

@app.route('/A4', methods=['POST'])
def runA4():
    if ser is None:
        return "Error: Arduino not connected."
    try:
        ser.write('A4\n'.encode())  # Send text to Arduino
        print("Sent to Arduino: A4")  # Debug log
    except Exception as e:
        print(f"Error: {e}")
    return redirect(url_for('index'))  # Redirect back to the main page

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
