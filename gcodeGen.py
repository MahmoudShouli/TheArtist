from PIL import Image
import numpy as np

def image_to_gcode(image_path, output_gcode_path):
    # Constants for the A4 paper size in landscape
    A4_WIDTH_MM = 297  # mm
    A4_HEIGHT_MM = 210  # mm
    DPI = 100  # Image resolution (dots per inch)
    PIXELS_PER_MM = DPI / 25.4  # Conversion factor

    # G-code settings
    PEN_DOWN_Z = 3.5
    PEN_UP_Z = 0
    FEEDRATE_DRAW = 2400
    FEEDRATE_MOVE = 1800

    # Load and process the image
    img = Image.open(image_path).convert("1")  # Convert to binary image (black and white)
    img = img.resize((int(A4_WIDTH_MM * PIXELS_PER_MM), int(A4_HEIGHT_MM * PIXELS_PER_MM)))
    img = np.array(img)

    # Prepare G-code
    gcode = []
    gcode.append("G21 ; Set units to mm")
    gcode.append("G90 ; Absolute positioning")

    # Generate G-code from image
    last_pen_state = "up"
    for y in range(img.shape[0]):
        for x in range(img.shape[1]):
            if img[y, x] == 0:  # Pixel is black
                x_mm = x / PIXELS_PER_MM
                y_mm = y / PIXELS_PER_MM

                if last_pen_state == "up":
                    # Pen down
                    gcode.append(f"G00 F{FEEDRATE_MOVE} X{x_mm:.2f} Y{y_mm:.2f}")
                    gcode.append(f"G00 Z{PEN_DOWN_Z:.1f}")
                    last_pen_state = "down"
                else:
                    # Drawing
                    gcode.append(f"G01 F{FEEDRATE_DRAW} X{x_mm:.2f} Y{y_mm:.2f}")
            elif last_pen_state == "down":
                # Pen up
                gcode.append(f"G00 Z{PEN_UP_Z:.1f}")
                last_pen_state = "up"

    # Ensure pen is up at the end
    if last_pen_state == "down":
        gcode.append(f"G00 Z{PEN_UP_Z:.1f}")

    # Write G-code to file
    with open(output_gcode_path, "w") as f:
        f.write("\n".join(gcode))

# Example usage
image_to_gcode("center.jpg", "output.gcode")
