import colorsys
from time import sleep
import sim
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2 
sim.simxFinish(-1)
clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)


# FUNCTIONS TO INTERFACE WITH THE ROBOT
def compress():
    sim.simxSetIntegerSignal(clientID=clientID, signalName="compress", signalValue=1,
                             operationMode=sim.simx_opmode_blocking)


def set_speed(speed_l, speed_r):
    sim.simxSetStringSignal(clientID=clientID, signalName="motors", signalValue=sim.simxPackFloats([speed_l, speed_r]),
                            operationMode=sim.simx_opmode_blocking)


def get_battery():
    return sim.simxGetStringSignal(clientID=clientID, signalName="battery",
                                   operationMode=sim.simx_opmode_blocking)


def get_bumper_sensor():
    # Bumper reading as 3-dimensional force vector
    bumper_force_vector = [0, 0, 0]
    return_code, bumper_force_vector_packed = sim.simxGetStringSignal(clientID=clientID, signalName="bumper_sensor",
                                                                      operationMode=sim.simx_opmode_blocking)
    if return_code == 0:
        bumper_force_vector = sim.simxUnpackFloats(bumper_force_vector_packed)
    return bumper_force_vector


def get_sonar_sensor():
    # Sonar reading as distance to closest object detected by it, -1 if no data
    sonar_dist = -1
    return_code, sonar_dist_packed = sim.simxGetStringSignal(clientID=clientID, signalName="sonar_sensor",
                                                             operationMode=sim.simx_opmode_blocking)
    if return_code == 0:
        sonar_dist = sim.simxUnpackFloats(sonar_dist_packed)
    return sonar_dist


def get_image_small_cam():
    # Image from the small camera
    return_code, return_value = sim.simxGetStringSignal(clientID=clientID, signalName="small_cam_image",
                                                        operationMode=sim.simx_opmode_blocking)
    if return_code == 0:
        image = sim.simxUnpackFloats(return_value)
        res = int(np.sqrt(len(image) / 3))
        return image_correction(image, res)
    else:
        return return_code


def get_image_top_cam():
    # Image from the top camera
    return_code, return_value = sim.simxGetStringSignal(clientID=clientID, signalName="top_cam_image",
                                                        operationMode=sim.simx_opmode_blocking)
    if return_code == 0:
        image = sim.simxUnpackFloats(return_value)
        res = int(np.sqrt(len(image) / 3))
        raw = image_correction(image, res)

        output = raw.astype(np.uint8)
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output
    else:
        return return_code


# HELPER FUNCTIONS
def image_correction(image, res):
    """
    This function can be applied to images coming directly out of CoppeliaSim.
    It turns the 1-dimensional array into a more useful res*res*3 array, with the first
    two dimensions corresponding to the coordinates of a pixel and the third dimension to the
    RGB values. Aspect ratio of the image is assumed to be square (1x1).

    :param image: the image as a 1D array
    :param res: the resolution of the image, e.g. 64
    :return: an array of shape res*res*3
    """

    image = [int(x * 255) for x in image]
    image = np.array(image).reshape((res, res, 3))
    image = np.flip(m=image, axis=0)
    return image


def show_image(image):
    plt.imshow(image)
    plt.show()

# END OF FUNCTIONS

def contains_yellow(image, yellow_threshold=10):
    """
    Classifies whether a given image contains yellow.
    """

    lower_yellow = np.array([0, 150, 150], dtype=np.uint8)
    upper_yellow = np.array([100, 255, 255], dtype=np.uint8)

    # Create a mask for yellow color
    yellow_mask = cv2.inRange(image, lower_yellow, upper_yellow)

    # show the mas
    # Count the number of yellow pixels
    yellow_pixel_count = np.count_nonzero(yellow_mask)

    # Determine if the image contains yellow based on the pixel count threshold
    contains_yellow = yellow_pixel_count > yellow_threshold

    return contains_yellow

def brown(cam):
    return [105, 52, 3] in cam()

def go_to_charge():
    speed = 4

    image = get_image_top_cam()
    image = image.astype(np.uint8)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    middle = int(len(image)/2)

    while not contains_yellow(image[:,middle-2:middle+2], 1):
        # turn in place until yellow is seen in the middle of the image
        set_speed(-speed, speed)
        image = get_image_top_cam()

    sleep(2)
    set_speed(30, 30)
    while not contains_yellow(image[:,middle-2:middle+2], 4*40):
        # go straight until yellow is seen in the bottom of the image
        image = get_image_top_cam()
    sleep(3)
    set_speed(0, 0)
    

# MAIN CONTROL LOOP
if clientID != -1:
    print('Connected')
    go_to_charge()
    while True:
        # your code goes here
        pass
        
        

       
    # zero, battery_info = get_battery()
    # percentage = float(battery_info.decode())
    # if percentage < 0.90:    
    #     set_speed(20, 100)   

    # End connection
    sim.simxGetPingTime(clientID)
    sim.simxFinish(clientID)
else:
    print('Failed connecting to remote API server')
print('Program ended')
