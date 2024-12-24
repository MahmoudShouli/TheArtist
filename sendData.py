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

@app.route('/A3', methods=['POST'])
def runA3():
    if ser is None:
        return "Error: Arduino not connected."
    try:
        ser.write('A3\n'.encode())  # Send text to Arduino
        return f"Sent to Arduino: A3"
    except Exception as e:
        return f"Error: {e}"
    

@app.route('/A4', methods=['POST'])
def runA4():
    if ser is None:
        return "Error: Arduino not connected."
    try:
        ser.write('A4\n'.encode())  # Send text to Arduino
        return f"Sent to Arduino: A4"
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
