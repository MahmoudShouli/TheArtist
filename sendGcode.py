import serial
import time

def configure_grbl(serial_port, gcode_commands,baud_rate=115200):
    """
    Configures GRBL settings by sending $ commands to the Arduino and sends a group of G-code commands.

    Parameters:
        serial_port (str): Serial port of the Arduino (e.g., /dev/ttyUSB0).
        baud_rate (int): Baud rate for the serial communication (default: 115200).
    """
    try:
        # Open serial connection to the Arduino
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser2:
            # Wake up GRBL
            ser2.write(b"\r\n\r\n")
            time.sleep(2)  # Wait for GRBL to initialize
            ser2.flushInput()  # Flush startup messages
            
            # Send the $$ command to list current settings
            ser2.write(b"$$\n")
            time.sleep(0.1)
            response = ser2.read_all().decode('utf-8')
            print("Current GRBL Settings:")
            print(response)
            
            
            for command in gcode_commands:
                ser2.write((command + "\n").encode('utf-8'))
                time.sleep(0.1)  # Wait for GRBL to process
                print(f"Sent G-code: {command}")
                print(ser2.readline().decode('utf-8').strip())  # Read GRBL response

    except Exception as e:
        print(f"Error: {e}")



