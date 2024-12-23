from flask import Flask, request, render_template
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

@app.route('/A4', methods=['POST'])
def send_to_arduino():
    if ser is None:
        return "Error: Arduino not connected."
    try:
        ser.write('User chose A4')  # Send text to Arduino
        return f"Sent to Arduino: {text}"
    except Exception as e:
        return f"Error: {e}"

@app.route('/A3', methods=['POST'])
def send_to_arduino():
    if ser is None:
        return "Error: Arduino not connected."
    try:
        ser.write('User chose A3')  # Send text to Arduino
        return f"Sent to Arduino: {text}"
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
