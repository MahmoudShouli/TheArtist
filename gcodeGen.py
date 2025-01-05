import cv2
import numpy as np

def image_to_gcode(image_path, output_gcode_path, paper_width_mm=210, paper_height_mm=297, pen_down_command="G00 Z3.5", pen_up_command="G00 Z0"):
    """
    Converts an image to G-code for CNC drawing on A4 paper.

    Parameters:
        image_path (str): Path to the input image.
        output_gcode_path (str): Path to save the generated G-code file.
        paper_width_mm (float): Width of the drawing area in mm (default: 210 mm for A4).
        paper_height_mm (float): Height of the drawing area in mm (default: 297 mm for A4).
        pen_down_command (str): G-code command for pen down.
        pen_up_command (str): G-code command for pen up.
    """
    # Load the image in grayscale
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image could not be loaded. Check the path.")

    # Resize image to fit A4 paper dimensions
    height, width = image.shape
    scale_x = paper_width_mm / width
    scale_y = paper_height_mm / height
    scale = min(scale_x, scale_y)
    new_width = int(width * scale)
    new_height = int(height * scale)
    resized_image = cv2.resize(image, (new_width, new_height))

    # Find contours in the binary image
    contours, _ = cv2.findContours(resized_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Initialize G-code commands
    gcode_commands = [
        "G21 ; Set units to mm",
        "G90 ; Absolute positioning",
        "G91 G0 F300.0 Z20.000 ; Pen park (Z-safe)",
        "G90 ; Absolute positioning",
        "G28 X ; Home X-axis",
        "G28 Y ; Home Y-axis",
        "G28 Z ; Home Z-axis"
    ]

    # Calculate the offsets to center the drawing on the paper
    offset_x = (paper_width_mm - new_width) / 2
    offset_y = (paper_height_mm - new_height) / 2

    for contour in contours:
        # Move to the starting point of the contour (pen up)
        start_point = contour[0][0]
        gcode_commands.append(f"G00 F2400.0 X{start_point[0] * scale + offset_x:.2f} Y{(new_height - start_point[1]) * scale + offset_y:.2f} ; Move to start")
        gcode_commands.append(pen_down_command)

        # Draw the contour (pen down)
        for point in contour:
            x, y = point[0]
            gcode_commands.append(f"G01 F2100.0 X{x * scale + offset_x:.2f} Y{(new_height - y) * scale + offset_y:.2f} ; Draw")

        # Pen up after finishing the contour
        gcode_commands.append(pen_up_command)

    # Add G-code end commands
    gcode_commands.extend([
        "G00 F2400.0 X0.00 Y0.00 ; Return to origin",
        "M30 ; End of program"
    ])

    # Save the G-code to a file
    with open(output_gcode_path, "w") as f:
        f.write("\n".join(gcode_commands))

    print(f"G-code saved to {output_gcode_path}")

# Example usage
image_to_gcode(
    image_path="center2.jpg", 
    output_gcode_path="output.gcode"
)
