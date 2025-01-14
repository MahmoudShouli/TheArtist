import serial
import time

try:
        # Open serial connection to the Arduino
        with serial.Serial('/dev/ttyACM1', 115200, timeout=1) as ser2:
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
            
            with open('blackPen.gcode', 'r') as f:
                black_pen_gcode = f.readlines() 
            
            for command in black_pen_gcode:
                ser2.write((command + "\n").encode('utf-8'))
                time.sleep(0.1)  # Wait for GRBL to process
                print(f"Sent G-code: {command}")
                print(ser2.readline().decode('utf-8').strip())  # Read GRBL response

    except Exception as e:
        print(f"Error: {e}")