import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage.util import invert
import matplotlib.pyplot as plt

def resize_to_fit(image, target_width, target_height):
    """
    Resize an image to fit within the target dimensions while maintaining aspect ratio.

    Parameters:
        image (np.ndarray): Input image.
        target_width (int): Target width in pixels.
        target_height (int): Target height in pixels.

    Returns:
        np.ndarray: Resized image.
    """
    height, width = image.shape[:2]
    scale = min(target_width / width, target_height / height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
    return resized_image

def centerline_trace(image_path, output_path):
    """
    Perform centerline tracing on an image and ensure it fits within A4 landscape dimensions.

    Parameters:
        image_path (str): Path to the input image.
        output_path (str): Path to save the resulting traced image.
    """
    # A4 dimensions in pixels (landscape, 300 DPI)
    A4_WIDTH = 3508
    A4_HEIGHT = 2480

    # Read the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Resize image to fit within A4 dimensions
    img_resized = resize_to_fit(img, A4_WIDTH, A4_HEIGHT)

    # Apply thresholding to create a binary image
    _, binary = cv2.threshold(img_resized, 127, 255, cv2.THRESH_BINARY_INV)

    # Normalize binary image to 0 and 1
    binary_normalized = binary // 255

    # Perform skeletonization
    skeleton = skeletonize(binary_normalized)

    # Convert skeleton back to 0-255 for saving
    skeleton_img = (skeleton * 255).astype(np.uint8)

    # Invert the skeleton for better visualization (optional)
    skeleton_inverted = invert(skeleton_img)

    # Create a blank A4 canvas
    canvas = np.full((A4_HEIGHT, A4_WIDTH), 255, dtype=np.uint8)

    # Center the processed image on the canvas
    skeleton_height, skeleton_width = skeleton_inverted.shape
    y_offset = (A4_HEIGHT - skeleton_height) // 2
    x_offset = (A4_WIDTH - skeleton_width) // 2
    canvas[y_offset:y_offset + skeleton_height, x_offset:x_offset + skeleton_width] = skeleton_inverted

    # Save the result
    cv2.imwrite(output_path, canvas)

    # Display the original and processed images
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title("Original Image")
    plt.imshow(img, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title("Centerline Traced Image (A4)")
    plt.imshow(canvas, cmap='gray')
    plt.axis('off')

    plt.show()

# Example usage
input_image_path = "static/photos/tawoos.jpg"  # Replace with your input image path
output_image_path = "center2.jpg"  # Replace with your output image path
centerline_trace(input_image_path, output_image_path)
