import cv2
import numpy as np
from skimage.morphology import skeletonize
from skimage.util import invert
import matplotlib.pyplot as plt

def centerline_trace(image_path, output_path):
    """
    Perform centerline tracing on an image.

    Parameters:
        image_path (str): Path to the input image.
        output_path (str): Path to save the resulting traced image.
    """
    # Read the image in grayscale
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Apply thresholding to create a binary image
    _, binary = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    # Normalize binary image to 0 and 1
    binary_normalized = binary // 255

    # Perform skeletonization
    skeleton = skeletonize(binary_normalized)

    # Convert skeleton back to 0-255 for saving
    skeleton_img = (skeleton * 255).astype(np.uint8)

    # Invert the skeleton for better visualization (optional)
    skeleton_inverted = invert(skeleton_img)

    # Save the result
    cv2.imwrite(output_path, skeleton_inverted)

    # Display the original and processed images
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.title("Original Image")
    plt.imshow(img, cmap='gray')
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.title("Centerline Traced Image")
    plt.imshow(skeleton_inverted, cmap='gray')
    plt.axis('off')

    plt.show()

# Example usage
input_image_path = "face.jpg"  # Replace with your input image path
output_image_path = "center.jpg"  # Replace with your output image path
centerline_trace(input_image_path, output_image_path)
