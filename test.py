import serial
import time

def configure_grbl(serial_port, baud_rate=115200):
    """
    Configures GRBL settings by sending $ commands to the Arduino and then sends a predefined array of G-code commands.

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
            
            # Update GRBL settings
            settings = [
                "$0=10",       # Step pulse time, microseconds
                "$1=25",       # Step idle delay, milliseconds
                "$2=0",        # Step pulse invert, mask
                "$3=0",        # Step direction invert, mask
                "$4=0",        # Invert step enable pin, boolean
                "$5=0",        # Invert limit pins, boolean
                "$6=0",        # Invert probe pin, boolean
                "$10=2",       # Status report options, mask
                "$11=0.010",   # Junction deviation, millimeters
                "$12=0.002",   # Arc tolerance, millimeters
                "$13=0",       # Report in inches, boolean
                "$20=0",       # Soft limits enable, boolean
                "$21=0",       # Hard limits enable, boolean
                "$22=0",       # Homing cycle enable, boolean
                "$23=0",       # Homing direction invert, mask
                "$24=25.000",  # Homing locate feed rate, mm/min
                "$25=750.000", # Homing search seek rate, mm/min
                "$26=250",     # Homing switch debounce delay, milliseconds
                "$27=1.000",   # Homing switch pull-off distance, millimeters
                "$30=1000",    # Maximum spindle speed, RPM
                "$31=0",       # Minimum spindle speed, RPM
                "$32=0",       # Laser-mode enable, boolean
                "$100=39.000", # X-axis travel resolution, step/mm
                "$101=68.200", # Y-axis travel resolution, step/mm
                "$102=400.000",# Z-axis travel resolution, step/mm
                "$110=2000.000",# X-axis maximum rate, mm/min
                "$111=2000.000",# Y-axis maximum rate, mm/min
                "$112=300.000",# Z-axis maximum rate, mm/min
                "$120=40.000", # X-axis acceleration, mm/sec^2
                "$121=40.000", # Y-axis acceleration, mm/sec^2
                "$122=10.000", # Z-axis acceleration, mm/sec^2
                "$130=332.000",# X-axis maximum travel, millimeters
                "$131=468.000",# Y-axis maximum travel, millimeters
                "$132=10.000", # Z-axis maximum travel, millimeters
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

            # Array of G-code commands to send
            gcode_commands = [
                "G10 L20 P1 X0 Y0 Z0",  # Set current position as origin
                "G90",                  # Set absolute positioning
                "G00 Y39",              # Move to Y39
                "G00 X300",             # Move to X300
                "G00 Z4.5",             # Move to Z4.5
                "G00 X308",             # Move to X308
                "M3 S0",                # Turn spindle off
                "G00 Z0",               # Move Z to 0
                "G00 X0 Y0"             # Move back to origin
            ]

            # Send G-code commands
            print("\nSending G-code commands:")
            for command in gcode_commands:
                ser.write((command + "\n").encode('utf-8'))
                time.sleep(0.1)  # Wait for GRBL to process the command
                print(f"Sent G-code: {command}")
                print(ser.readline().decode('utf-8').strip())  # Read GRBL response

    except Exception as e:
        print(f"Error: {e}")

# Example usage
configure_grbl(serial_port="/dev/ttyACM0")  # Adjust serial port as needed
