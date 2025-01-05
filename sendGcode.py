import serial
import time

def send_gcode_to_grbl(gcode_file_path, serial_port, baud_rate=9600):
    """
    Sends G-code commands from a file to an Arduino running GRBL.

    Parameters:
        gcode_file_path (str): Path to the G-code file.
        serial_port (str): Serial port of the Arduino (e.g., /dev/ttyUSB0).
        baud_rate (int): Baud rate for the serial communication (default: 115200).
    """
    # Open serial connection to the Arduino
    try:
        with serial.Serial(serial_port, baud_rate, timeout=1) as ser:
            # Wake up GRBL
            ser.write(b"\r\n\r\n")
            time.sleep(2)  # Wait for GRBL to initialize
            ser.flushInput()  # Flush startup messages
            
            # Open G-code file
            with open(gcode_file_path, "r") as gcode_file:
                for line in gcode_file:
                    # Strip whitespace and comments
                    command = line.strip().split(';')[0]
                    if command:
                        # Send G-code command to GRBL
                        print(f"Sending: {command}")
                        ser.write((command + "\n").encode('utf-8'))
                        
                        # Wait for GRBL response
                        response = ser.readline().decode('utf-8').strip()
                        print(f"Response: {response}")
                        
                        # Pause between commands to prevent buffer overflow
                        time.sleep(0.1)
            print("G-code file sent successfully.")
    except Exception as e:
        print(f"Error: {e}")

# Example usage
send_gcode_to_grbl(
    gcode_file_path="output.gcode",  # Path to your G-code file
    serial_port="/dev/ttyACM0"       # Adjust based on your setup
)
