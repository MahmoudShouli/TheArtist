import serial
import time
import cv2

def generate_gcode(image_path, page_size):
    # Load the processed image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Detect contours
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Determine scaling based on page size (portrait orientation)
    if page_size == "A3":
        max_width, max_height = 420.0, 297.0  # in mm (portrait orientation)
    elif page_size == "A4":
        max_width, max_height = 297.0, 210.0  # in mm (portrait orientation)
    else:
        raise ValueError("Invalid page size. Choose 'A3' or 'A4'.")

    # Get bounding box of contours
    x_min, y_min, x_max, y_max = float('inf'), float('inf'), 0, 0
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + w)
        y_max = max(y_max, y + h)

    # Calculate scaling factor
    width, height = x_max - x_min, y_max - y_min
    scale_x = max_width / width
    scale_y = max_height / height
    scale = min(scale_x, scale_y)

    # Generate G-code
    gcode = []

    for contour in contours:
        for i, point in enumerate(contour):
            x, y = point[0][0], point[0][1]

            # Scale points
            x = (x - x_min) * scale
            y = (y - y_min) * scale

            if i == 0:
                # Move to the starting point
                gcode.append(f"G00 F1800.0 X{x:.3f} Y{y:.3f}")
            else:
                # Draw line to the next point
                gcode.append(f"G01 F1200.0 X{x:.3f} Y{y:.3f}")

    # Add footer to return to origin
    gcode.append("G00 X0 Y0")

    # Save the G-code to a file
    with open("drawing.gcode", "w") as f:
        f.write("\n".join(gcode))

    return gcode
    

def configure_grbl(serial_port, gArray, isSettings, baud_rate=115200):
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

            # if isSettings:
            #     for setting in settings:
            #         serUno.write((setting + "\n").encode('utf-8'))
            #         time.sleep(0.1)
            #         print(f"Set: {setting}")
            #         print(serUno.readline().decode('utf-8').strip())  # Read GRBL response
            


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
                if isSettings:
                    time.sleep(0.5)

    except Exception as e:
        print(f"Error: {e}")

    print("All commands completed successfully")
    return True

