import cv2
import numpy as np
from skimage.morphology import skeletonize

# Constants for G-code generation
PEN_UP_Z = 0  # Pen up position
PEN_DOWN_Z = 3.5  # Pen down position
FEED_RATE_G00 = 1800  # Feed rate for G00
FEED_RATE_G01 = 2400  # Feed rate for G01
A4_WIDTH = 297  # A4 paper width in mm (landscape)
A4_HEIGHT = 210  # A4 paper height in mm (landscape)
MARGIN = 10  # Margin from edges in mm

# Function to scale coordinates to fit A4 landscape paper
def scale_to_a4(coords, img_shape):
    img_h, img_w = img_shape[:2]
    scale_w = (A4_WIDTH - 2 * MARGIN) / img_w
    scale_h = (A4_HEIGHT - 2 * MARGIN) / img_h
    scale = min(scale_w, scale_h)
    
    scaled_coords = []
    for x, y in coords:
        scaled_x = MARGIN + x * scale
        scaled_y = MARGIN + y * scale
        scaled_coords.append((scaled_x, scaled_y))
    return scaled_coords

# Function to extract skeletonized coordinates from an image
def extract_skeleton_coords(image_path):
    # Load the image
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Invert the image if necessary (ensure black background and white foreground)
    if np.mean(image) > 127:
        image = cv2.bitwise_not(image)

    # Binarize the image
    _, binary = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)

    # Skeletonize the binary image
    skeleton = skeletonize(binary // 255)

    # Extract the coordinates of the skeleton
    coords = np.column_stack(np.where(skeleton > 0))
    return coords, binary.shape

# Function to generate G-code from coordinates
def generate_gcode(coords):
    gcode = []

    # Move to the first point (pen up)
    gcode.append(f"G00 Z{PEN_UP_Z}")
    for i, (x, y) in enumerate(coords):
        if i == 0 or coords[i - 1] != (x, y):  # Move if the point changes
            gcode.append(f"G00 F{FEED_RATE_G00} X{x:.2f} Y{y:.2f}")
            gcode.append(f"G00 Z{PEN_DOWN_Z}")
        gcode.append(f"G01 F{FEED_RATE_G01} X{x:.2f} Y{y:.2f}")

    # Pen up at the end
    gcode.append(f"G00 Z{PEN_UP_Z}")
    return gcode

# Main function to process the image and generate G-code
def image_to_gcode(image_path, output_path):
    coords, img_shape = extract_skeleton_coords(image_path)
    scaled_coords = scale_to_a4(coords, img_shape)
    gcode = generate_gcode(scaled_coords)

    # Write G-code to file
    with open(output_path, 'w') as f:
        f.write("\n".join(gcode))

# Example usage
if __name__ == "__main__":
    input_image = "input_image.png"  # Replace with your input image path
    output_gcode = "output.gcode"  # Replace with your desired G-code output path
    image_to_gcode(input_image, output_gcode)
    print(f"G-code generated and saved to {output_gcode}")
