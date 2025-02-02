import cv2
import numpy as np

image = cv2.imread('./static/photos/ss.jpg')

   
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


lower_green = np.array([40, 100, 50])
upper_green = np.array([90, 255, 255])


mask = cv2.inRange(hsv, lower_green, upper_green)
mask_inv = cv2.bitwise_not(mask)


white_background = np.full_like(image, 255, dtype=np.uint8)
result = np.where(mask[:, :, None].astype(bool), white_background, image)


sharpening_kernel = np.array([[0, -0.3, 0], [-0.3, 2, -0.3], [0, -0.3, 0]])
sharpened_image = cv2.filter2D(result, -1, sharpening_kernel)


brightness_factor = 20  
brightened_image = cv2.add(sharpened_image, np.array([brightness_factor], dtype=np.uint8))


cv2.imwrite('./testoutput.jpg', brightened_image)