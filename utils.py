import cv2 
import numpy as np
def detect_color_coordinates(image, lower_color, upper_color):
    lower_bound = np.array(lower_color, dtype=np.uint8)
    upper_bound = np.array(upper_color, dtype=np.uint8)

    # Create a mask for the target color
    mask = cv2.inRange(image, lower_bound, upper_bound)
    cv2.imshow('mask', mask)
    cv2.waitKey(1)
    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Initialize variables for calculating average coordinates
    total_x = 0
    total_y = 0
    count = 0

    # Iterate over the contours and calculate average coordinates
    for contour in contours:
        # Calculate the center of each contour
        M = cv2.moments(contour)
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Add the coordinates to the total
            total_x += cX
            total_y += cY
            count += 1

    # Calculate the average coordinates
    if count > 0:
        avg_x = total_x / count
        avg_y = total_y / count
        avg_coordinates = (avg_x, avg_y)
    else:
        avg_coordinates = None

    return avg_coordinates


def contains_color(image, lower_color, upper_color, threshold=10):
    lower_yellow = np.array(lower_color, dtype=np.uint8)
    upper_yellow = np.array(upper_color, dtype=np.uint8)

    # Create a mask for target color
    mask = cv2.inRange(image, lower_yellow, upper_yellow)

    # show the mas
    # Count the number of pixels
    pixel_count = np.count_nonzero(mask)

    # Determine if the image contains yellow based on the pixel count threshold
    contains_color = pixel_count > threshold

    return contains_color