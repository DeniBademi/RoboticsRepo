import colorsys
import random
from time import sleep
import time
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

    error = detect_color_coordinates(image, CHARGER)[0] - middle

    if error is None:
        return

    # to do: while it is not charging
    battery = get_battery()
    while(get_battery()<=battery):
        image = get_image_top_cam()
        error = (detect_color_coordinates(image, CHARGER)[0] - middle) * speed/10

        if error is None:
            return
        
        if abs(error) < 2:
            #go straight
            set_speed(speed, speed)
            continue
        set_speed(speed + error, speed -error)

    set_speed(0,0)
    while get_battery() < 0.95:
        pass

def is_carrying_object():
    image = get_image_small_cam()
    middle = int(len(image)/2)
    
    show_mask(image[-3:-1, :], COMPRESSED, 1)
    return ((contains_object(image, TRASH, 62**2) \
    or contains_object(image, TRASH_2, 62**2) \
    or contains_object(image, PLANT, 62**2)) \
    and get_sonar_sensor()[0] < 0.2) \
    or contains_object(image[-3:-1, :], COMPRESSED, 30)


def find_compressed_object():
    print("finding compressed object")
    image = get_image_small_cam()
    middle = int(len(image)/2)

    set_speed(30, 30)
    sleep(0.4)

    time_s = time.time()
    
    set_speed(-30, 30)
    while not contains_object(image[middle+10:,middle-3:middle+3], COMPRESSED, 1):
        # cv2.imshow("image", image[middle:,middle-3:middle+3])
        # cv2.waitKey(1)
        # cv2.imshow("img", image[middle+3:,middle-3:middle+3])
        # cv2.waitKey(1)
        image = get_image_small_cam()
        if time.time() - time_s > 10:
            print("could not find compressed object")
            return 1

    print("found compressed object, going to it")
    set_speed(30, 30)
    sleep(2)
    return 0
        
        



def go_to_dropoff(object: Entity):

    dropoff = PLANT_COLLECTOR if object.name == "PLANT" else TRASH_COLLECTOR
    speed = 30
    image = get_image_top_cam()
    middle = int(len(image)/2)
    status = 0

    if object in [TRASH, TRASH_2]:
        compress()
        print("not carrying object, finding compressed object")
        status = find_compressed_object()

    if status == 1:
        return

    while not contains_object(image, dropoff):
        set_speed(speed, speed*2)
        image = get_image_top_cam()
        show_mask(image, WALL, 1)

        if contains_object(image, WALL, 55**2):
            set_speed(-speed*0.5, -speed*2)
            sleep(2)
            return

    error = detect_color_coordinates(image, dropoff)[0] - middle

    while is_carrying_object():
        image = get_image_top_cam()
        # cv2.imshow("image", image)
        # cv2.waitKey(1)


        
        target = detect_color_coordinates(image, dropoff)
        if target is None:
            set_speed(speed, 2*speed)
            continue
        error = (target[0] - middle) * speed/50

        # Obstacle avoidance
        middle = int(len(image)/2)
        if detect_object(image[:middle+10,10:-10], [TRASH, TRASH_2, PLANT], 160)[0] is not None:
            error +=10
            set_speed(speed + error, speed -error)
            sleep(2)
            continue

        if contains_object(image, WALL, 45**2):
            set_speed(-speed*0.5, -speed*2)
            sleep(2)
            return


        print(error)
        # if abs(error) < 5:
        #     #go straight
        #     set_speed(speed, speed)
        #     continue
        set_speed(speed + error, speed -error)

        show_mask(get_image_small_cam(), object, 1)
    set_speed(-speed, -speed)
    sleep(3)
    set_speed(speed, -speed)
    sleep(3)


def go_to_object(object: Entity):
    speed = 300
    image = get_image_top_cam()
    middle = int(len(image)/2)

    if object == COMPRESSED:
        image = image[middle:,middle-10:middle+10] # only look at the bottom half of the image 

    # Spin until the target object is in visual field
    while not contains_object(image, object, 1):
        set_speed(-speed, speed)
        image = get_image_top_cam()
        if object == COMPRESSED:
            image = image[middle:,middle-10:middle+10]

    # Stop spinning
    set_speed(0,0)

    image = get_image_top_cam()
    if object == COMPRESSED:
        image = image[middle:,middle-10:middle+10]

    # Get exact coordinates of target object on the image 
    target = detect_object(image, [object], 1)

    if target[0] is None:
        print("object not found")
        # cv2.imshow("image", image)
        # cv2.waitKey(0)
        return

    error = (target[1] - middle) * speed/50

    
    # Move towards the object until it is in carry position. Adjust robot's trajectory to
    # bring the object in the vertical middle of the image
    while not is_carrying_object():
        image = get_image_top_cam()

        if object == COMPRESSED:
            image = image[middle:,middle-10:middle+10] # only look at the bottom half of the image 
        target = detect_object(image, [object])

        if target[0] is None:
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

    image_top = get_image_top_cam()
    image_small = get_image_small_cam()



    set_speed(speed + error, speed -error)
    sleep(duration)

def stay_alive():

    image_top = get_image_top_cam()
    image_small = get_image_small_cam()
    speed = 30

    if contains_object(image_small, WALL, 62**2) \
        or contains_object(image_top, PLANT_COLLECTOR, 40**2) \
        or contains_object(image_top, TRASH_COLLECTOR, 40**2):
        set_speed(-speed, -speed)
        sleep(3)
        set_speed(speed, -speed)
        sleep(2)
    
current_behavior = None

# MAIN CONTROL LOOP
if clientID != -1:
    print('Connected')
    
    set_speed(0,0)
    object = None
    while True:

        
        # set_speed(0,0)
        #print(get_image_top_cam()[40][40])
        # show_mask(get_image_top_cam(), TRASH_COLLECTOR, 1)

        # #print(is_carrying_object())
        # # if is_carrying_object():


        # print(current_behavior)

        
        stay_alive()

        if get_battery() < 0.20:
            current_behavior = "go_to_charge"
            print(current_behavior)
            go_to_charge()
        
        elif is_carrying_object() and object is not None:
            current_behavior = "carrying_object " + object.name
            print(current_behavior)
            go_to_dropoff(object)
        else:
            
            object = detect_object(get_image_top_cam())[0]
            if object is not None:
                current_behavior = "going_to_object " + object.name
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
