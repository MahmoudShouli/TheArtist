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
                "G10 L20 P1 X0 Y0 Z0",      
                "G90",     
                "G0 y39",     
                "G00 Z4.5",     
                "g00 x308",       
                "M3 S0",
                "g00 z0",
                "g00 x0 y0"     
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
