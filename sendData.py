import serial
import time

arduino_port = '/dev/ttyACM0'  # Adjust if necessary
baud_rate = 9600

try:
    ser = serial.Serial(arduino_port, baud_rate, timeout=1)
    print(f"Connected to Arduino on {arduino_port}")
    
    while True:
        message = input("Enter a message to send to Arduino (or 'exit' to quit): ")
        if message.lower() == 'exit':
            break
        ser.write(message.encode())
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    ser.close()
    print("Serial connection closed.")
