import serial
import time

def configure_grbl(serial_port, gArray, baud_rate=115200):
    """
    Configures GRBL settings by sending $ commands to the Arduino and then sends a predefined array of G-code commands.

    Parameters:
        serial_port (str): Serial port of the Arduino (e.g., /dev/ttyUSB0).
        baud_rate (int): Baud rate for the serial communication (default: 115200).
    """
    try:
        # Open serial connection to the Arduino
        with serial.Serial(serial_port, baud_rate, timeout=1) as serUno:
            # Wake up GRBL
            serUno.write(b"\r\n\r\n")
            time.sleep(2)  # Wait for GRBL to initialize
            serUno.flushInput()  # Flush startup messages
            
            # Send the $$ command to list current settings
            serUno.write(b"$$\n")
            time.sleep(0.1)
            response = serUno.read_all().decode('utf-8')
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
                serUno.write((setting + "\n").encode('utf-8'))
                time.sleep(0.1)
                print(f"Set: {setting}")
                print(serUno.readline().decode('utf-8').strip())  # Read GRBL response
            
            # Verify updated settings
            serUno.write(b"$$\n")
            time.sleep(0.1)
            response = serUno.read_all().decode('utf-8')
            print("Updated GRBL Settings:")
            print(response)


            # Send G-code commands
            print("\nSending G-code commands:")
            for command in gArray:
                serUno.write((command + "\n").encode('utf-8'))
                print(f"Sent G-code: {command}")
                while True:
                    response = serUno.readline().decode('utf-8').strip()
                    if response:
                        print(response)
                    if response == "ok":
                        break

    except Exception as e:
        print(f"Error: {e}")

    print("All commands completed successfully")
    return True

