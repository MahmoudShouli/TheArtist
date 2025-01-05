import serial
import time

def configure_grbl(serial_port, baud_rate=9600):
    """
    Configures GRBL settings by sending $ commands to the Arduino.

    Parameters:
        serial_port (str): Serial port of the Arduino (e.g., /dev/ttyUSB0).
        baud_rate (int): Baud rate for the serial communication (default: 115200).
    """
    try:
        # Open serial connection to the Arduino
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
            # Wake up GRBL
            ser.write(b"\r\n\r\n")
            time.sleep(2)  # Wait for GRBL to initialize
            ser.flushInput()  # Flush startup messages
            
            # Send the $$ command to list current settings
            ser.write(b"$$\n")
            time.sleep(0.1)
            response = ser.read_all().decode('utf-8')
            print("Current GRBL Settings:")
            print(response)
            
            # Example: Update GRBL settings (adjust these commands as needed)
            settings = [
                "$100=250.0",  # X-axis steps/mm
                "$101=250.0",  # Y-axis steps/mm
                "$102=250.0",  # Z-axis steps/mm
                "$110=5000",   # X-axis max rate
                "$111=5000",   # Y-axis max rate
                "$112=5000",   # Z-axis max rate
            ]
            
            for setting in settings:
                ser.write((setting + "\n").encode('utf-8'))
                time.sleep(0.1)
                print(f"Set: {setting}")
                print(ser.readline().decode('utf-8').strip())  # Read GRBL response
            
            # Verify updated settings
            ser.write(b"$$\n")
            time.sleep(0.1)
            response = ser.read_all().decode('utf-8')
            print("Updated GRBL Settings:")
            print(response)
    except Exception as e:
        print(f"Error: {e}")

# Example usage
configure_grbl(serial_port="/dev/ttyACM0")  # Adjust serial port as needed
