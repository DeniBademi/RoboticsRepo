import colorsys
import random
from time import sleep
import sim
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2 
from utils import *
from settings import *

sim.simxFinish(-1)
clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)



def compress():
    sim.simxSetIntegerSignal(clientID=clientID, signalName="compress", signalValue=1,
                             operationMode=sim.simx_opmode_blocking)


def set_speed(speed_l, speed_r):
    sim.simxSetStringSignal(clientID=clientID, signalName="motors", signalValue=sim.simxPackFloats([speed_l, speed_r]),
                            operationMode=sim.simx_opmode_blocking)


def get_battery():
    return float(sim.simxGetStringSignal(clientID=clientID, signalName="battery",
                                   operationMode=sim.simx_opmode_blocking)[1].decode())


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
        raw = image_correction(image, res)

        output = raw.astype(np.uint8)
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
        return output
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

# def contains_charger(image, yellow_threshold=10):
#     return contains_color(image, CHARGER.lower_color, CHARGER.upper_color, yellow_threshold)

# def contains_trash(image, brown_threshold=10):
#     return contains_color(image, TRASH.lower_color, TRASH.upper_color, brown_threshold)

# def contains_trash_2(image, red_threshold=10):
#     return contains_color(image, TRASH_2.lower_color, TRASH_2.upper_color, red_threshold)

# def contains_plant_collector(image, blue_threshold=10):
#     return contains_color(image, PLANT_COLLECTOR.lower_color, PLANT_COLLECTOR.upper_color, blue_threshold)

# def contains_trash_collector(image, threshold=10):
#     return contains_color(image, PLANT.lo, [40, 40, 255], threshold)



def go_to_charge():

    speed = 30

    image = get_image_top_cam()

    middle = int(len(image)/2)

    while not contains_object(image[:,middle-2:middle+2], CHARGER, 1):
        # turn in place until yellow is seen in the middle of the image
        set_speed(-speed, speed)
        image = get_image_top_cam()

    sleep(2)

    error = detect_color_coordinates(image, CHARGER)[0] - middle


    # to do: while it is not charging
    while(not contains_object(image[:,middle-2:middle+2], CHARGER, 4*40)):
        image = get_image_top_cam()
        error = (detect_color_coordinates(image, CHARGER)[0] - middle) * speed/10
        if abs(error) < 2:
            #go straight
            set_speed(speed, speed)
            continue
        set_speed(speed + error, speed -error)

def is_carrying_object():
    image = get_image_small_cam()
    middle = int(len(image)/2)
    
    return (contains_object(image, TRASH, 62**2) \
    or contains_object(image, TRASH_2, 62**2) \
    or contains_object(image, PLANT, 62**2) \
    or contains_object(image[middle:,:], COMPRESSED, 1)) \
    or get_sonar_sensor()[0] < 0.18


def find_compressed_object():
    print("finding compressed object")
    image = get_image_small_cam()
    middle = int(len(image)/2)

    set_speed(30, 0)
    while not contains_object(image[middle+3:,middle-3:middle+3], COMPRESSED, 1):
        # cv2.imshow("image", image[middle:,middle-3:middle+3])
        # cv2.waitKey(1)
        image = get_image_small_cam()

    print("found compressed object, going to it")
    set_speed(30, 30)
    sleep(2)
        
        



def go_to_dropoff(object: Entity):

    dropoff = PLANT_COLLECTOR if object.name == "PLANT" else TRASH_COLLECTOR
    speed = 30
    image = get_image_top_cam()
    middle = int(len(image)/2)

    while not contains_object(image, dropoff):
        set_speed(speed, speed*2)
        image = get_image_top_cam()

        if object in [TRASH, TRASH_2]:
            compress()
            if not is_carrying_object():
                print("not carrying object, finding compressed object")
                find_compressed_object()
                break

    if object in [TRASH, TRASH_2]:
        while not contains_object(image, dropoff):
            set_speed(speed, speed*2)
            image = get_image_top_cam()

    error = detect_color_coordinates(image, dropoff)[0] - middle

    while (not contains_object(get_image_small_cam(), dropoff, 53**2)) or get_sonar_sensor()[0] > 0.18:
        image = get_image_top_cam()
        # cv2.imshow("image", image)
        # cv2.waitKey(1)
        error = (detect_color_coordinates(image, dropoff)[0] - middle) * speed/50
        print(error)
        if abs(error) < 5:
            #go straight
            set_speed(speed, speed)
            continue
        set_speed(speed + error, speed -error)
    set_speed(-speed, -speed)
    sleep(3)
    set_speed(speed, -speed)
    sleep(3)


def go_to_object(object: Entity):
    speed = 30
    image = get_image_top_cam()
    middle = int(len(image)/2)

    if object == COMPRESSED:
        image = image[middle:,middle-10:middle+10] # only look at the bottom half of the image 


    while not contains_object(image, object, 1):
        # turn in place until yellow is seen in the middle of the image
        set_speed(-speed, speed)
        image = get_image_top_cam()
        if object == COMPRESSED:
            image = image[middle:,middle-10:middle+10] # only look at the bottom half of the image 


    set_speed(0,0)

    image = get_image_top_cam()
    if object == COMPRESSED:
        image = image[middle:,middle-10:middle+10]

    target = detect_object(image, [object], 1)

    if target[0] is None:
        print("object not found")
        # cv2.imshow("image", image)
        # cv2.waitKey(0)
        return

    error = (target[1] - middle) * speed/50

    # not contains_object(image[:,middle-2:middle+2], object, 4*40)
    while not is_carrying_object():
        image = get_image_top_cam()
       
        # cv2.imshow("image", image)
        # cv2.waitKey(1)

        if object == COMPRESSED:
            image = image[middle:,middle-10:middle+10] # only look at the bottom half of the image 
        target = detect_object(image, [object])

        if target is None:
            return
        
        error = (target[1] - middle) * speed/50
        if abs(error) < 2:
            #go straight
            set_speed(speed, speed)
            continue

        set_speed(speed + error, speed -error)

    set_speed(0,0)


def print_color():

    image = get_image_top_cam()
    middle = int(len(image)/2)
    
    while True:
        print(show_mask(image, TRASH, 1))
        print(image[0][-1])
        # cv2.imshow('image', image)
        # cv2.waitKey(1)
        image = get_image_top_cam()



def wander():
    speed = 30
    
    error = random.randint(-10, 10)
    duration = random.randint(1, 5)

    set_speed(speed + error, speed -error)
    sleep(duration)

    
current_behavior = None

# MAIN CONTROL LOOP
if clientID != -1:
    print('Connected')
    
    object = None
    while True:

        print(current_behavior)
        if get_battery() < 0.20:
            current_behavior = "go_to_charge"
            print(current_behavior)
            go_to_charge()
        
        elif is_carrying_object():
            current_behavior = "carrying_object"
            print(current_behavior)
            go_to_dropoff(object)
        else:
            
            object = detect_object(get_image_top_cam())[0]
            if object is not None:
                current_behavior = "going_to_object"
                print(current_behavior)
                go_to_object(object)
            else:
                current_behavior = "wandering"
                wander()


    

    # if battery is low:
    # go to charge
    # else:
    # if carrying object:
    # go to dropoff
    # else:
    # if object in sight:
    # go to object
    # else:
    # wander
        

       
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
