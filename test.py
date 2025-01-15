import serial
import time

def configure_grbl(serial_port, baud_rate=115200):
    """
    Configures GRBL settings by sending $ commands to the Arduino and sends a sequence of G-code commands.

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
            
            
            # Send the sequence of G-code commands
            gcode_commands = [
                "G10 L20 P1 X0 Y0 Z0",      # Move to Y39
                "G90",     # Move to X300
                "G0 X100",     # Move to Z4.5
                "G0 X200",     # Move to X308
                "M3 S0",        # Turn spindle off
                "G00 X0 Y0"     # Move back to the origin (0,0)
            ]
            
            for command in gcode_commands:
                ser.write((command + "\n").encode('utf-8'))
                time.sleep(0.1)  # Wait for GRBL to process
                print(f"Sent G-code: {command}")
                print(ser.readline().decode('utf-8').strip())  # Read GRBL response

    except Exception as e:
        print(f"Error: {e}")

# Example usage
configure_grbl(serial_port="/dev/ttyACM0")  # Adjust serial port as needed
