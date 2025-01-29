import serial
import time
import cv2



def wait_for_idle(serUno):
    """Waits until GRBL reports 'Idle' status, meaning all commands have been executed."""
    while True:
        serUno.write(b"?\n")  # Send status request
        time.sleep(0.1)  # Small delay to prevent flooding GRBL
        response = serUno.readline().decode('utf-8').strip()
        
        if "Idle" in response:
            print("GRBL is now idle.")
            break    


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
                "$110=1500.000",# X-axis maximum rate, mm/min
                "$111=1500.000",# Y-axis maximum rate, mm/min
            ]

            drawing_settings = [
                "$110=800.000",# X-axis maximum rate, mm/min
                "$111=800.000",# Y-axis maximum rate, mm/min
            ]

            if isSettings:
                for setting in settings:
                    serUno.write((setting + "\n").encode('utf-8'))
                    time.sleep(0.1)
                    print(f"Set: {setting}")
                    print(serUno.readline().decode('utf-8').strip())  # Read GRBL response

            else:
                for setting in drawing_settings:
                    serUno.write((setting + "\n").encode('utf-8'))
                    time.sleep(0.1)
                    print(f"Set: {setting}")
                    print(serUno.readline().decode('utf-8').strip())
            


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

            wait_for_idle(serUno)

    except Exception as e:
        print(f"Error: {e}")

    print("All commands completed successfully")
    return True

