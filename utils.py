import cv2 
import numpy as np

from settings import *

def detect_color_coordinates(image, object: Entity):
    lower_bound = np.array(object.lower_color, dtype=np.uint8)
    upper_bound = np.array(object.upper_color, dtype=np.uint8)

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

def detect_object(image, detectable_objects = [TRASH, TRASH_2, PLANT], threshold=1):

    optimal_objects = []

    for object in detectable_objects:
        lower_bound = np.array(object.lower_color, dtype=np.uint8)
        upper_bound = np.array(object.upper_color, dtype=np.uint8)

        # Create a mask for the target color
        mask = cv2.inRange(image, lower_bound, upper_bound)
    
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
        if len(contours) == 0:
            continue
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
    
        # Calculate the coordinates of the bounding rectangle for the largest contour
        x, y, w, h = cv2.boundingRect(largest_contour)
        centerX = x + w / 2
        optimal_objects.append((object, centerX, w*h))


    optimal_objects.sort(key=lambda x: x[2], reverse=True)

    if len(optimal_objects) > 0 and optimal_objects[0][2] > threshold:
        return optimal_objects[0]
    else:
        return (None, None, None)


def contains_object(image, object, threshold=10):

    
    lower_yellow = np.array(object.lower_color, dtype=np.uint8)
    upper_yellow = np.array(object.upper_color, dtype=np.uint8)

    # Create a mask for target color
    mask = cv2.inRange(image, lower_yellow, upper_yellow)
    # cv2.imshow('mask', mask)
    # cv2.waitKey(1)
    # show the mas
    # Count the number of pixels
    pixel_count = np.count_nonzero(mask)

    # Determine if the image contains yellow based on the pixel count threshold
    contains_color = pixel_count > threshold

    return contains_color


def show_mask(image, object, threshold=10):

    
    lower = np.array(object.lower_color, dtype=np.uint8)
    upper = np.array(object.upper_color, dtype=np.uint8)

    # Create a mask for target color
    mask = cv2.inRange(image, lower, upper)
    cv2.imshow('mask', mask)
    cv2.waitKey(1)


