import cv2
import numpy as np
import matplotlib.pyplot as plt

def gaussian_smoothing(image, sigma=2):
    # Apply Gaussian blur to smooth the image
    return cv2.GaussianBlur(image, (5, 5), sigma)

def compute_gradients(image):
    # Compute the gradients in the X and Y directions
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    # Compute the gradient magnitude
    magnitude = np.sqrt(grad_x**2 + grad_y**2)
    return grad_x, grad_y, magnitude

def non_maximum_suppression(gradient_magnitude, gradient_direction):
    # Suppress non-maximum pixels in the gradient magnitude image
    rows, cols = gradient_magnitude.shape
    suppressed = np.zeros((rows, cols), dtype=np.float64)
    
    angle = gradient_direction * 180.0 / np.pi
    angle[angle < 0] += 180

    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            try:
                q, r = 255, 255
                # Angle 0 degrees
                if (0 <= angle[i, j] < 22.5) or (157.5 <= angle[i, j] <= 180):
                    q = gradient_magnitude[i, j + 1]
                    r = gradient_magnitude[i, j - 1]
                # Angle 45 degrees
                elif 22.5 <= angle[i, j] < 67.5:
                    q = gradient_magnitude[i + 1, j - 1]
                    r = gradient_magnitude[i - 1, j + 1]
                # Angle 90 degrees
                elif 67.5 <= angle[i, j] < 112.5:
                    q = gradient_magnitude[i + 1, j]
                    r = gradient_magnitude[i - 1, j]
                # Angle 135 degrees
                elif 112.5 <= angle[i, j] < 157.5:
                    q = gradient_magnitude[i - 1, j - 1]
                    r = gradient_magnitude[i + 1, j + 1]

                if gradient_magnitude[i, j] >= q and gradient_magnitude[i, j] >= r:
                    suppressed[i, j] = gradient_magnitude[i, j]
                else:
                    suppressed[i, j] = 0

            except IndexError as e:
                pass

    return suppressed

def hysteresis_threshold(image, low_threshold, high_threshold):
    # Apply hysteresis thresholding
    weak = 50
    strong = 255

    strong_i, strong_j = np.where(image >= high_threshold)
    weak_i, weak_j = np.where((image <= high_threshold) & (image >= low_threshold))

    result = np.zeros_like(image, dtype=np.uint8)
    result[strong_i, strong_j] = strong
    result[weak_i, weak_j] = weak

    rows, cols = image.shape
    for i in range(1, rows - 1):
        for j in range(1, cols - 1):
            if result[i, j] == weak:
                if (
                    strong in result[i - 1 : i + 2, j - 1 : j + 2]
                ):
                    result[i, j] = strong
                else:
                    result[i, j] = 0

    return result

# Main Canny Edge Detection function
def canny_edge_detector(image, sigma=2, low_threshold=0, high_threshold=30):
    # Step 1: Gaussian Smoothing
    smoothed = gaussian_smoothing(image, sigma)

    # Step 2: Compute Gradients
    grad_x, grad_y, magnitude = compute_gradients(smoothed)
    direction = np.arctan2(grad_y, grad_x)

    # Step 3: Non-Maximum Suppression
    nms = non_maximum_suppression(magnitude, direction)

    # Step 4: Hysteresis Thresholding
    edges = hysteresis_threshold(nms, low_threshold, high_threshold)

    return edges

# Load an image in grayscale
image = cv2.imread('./static/photos/photo.jpg', cv2.IMREAD_GRAYSCALE)

# Run the Canny Edge Detector
edges = canny_edge_detector(image)

# Display the results
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.title("Original Image")
plt.imshow(image, cmap='gray')

plt.subplot(1, 2, 2)
plt.title("Canny Edges")
plt.imshow(edges, cmap='gray')

plt.show()
