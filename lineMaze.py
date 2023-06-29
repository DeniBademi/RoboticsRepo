import sim
import matplotlib.pyplot as plt
from mindstorms import Motor, Direction, ColorSensor
import time
sim.simxFinish(-1)
clientID = sim.simxStart('127.0.0.1', 19999, True, True, 5000, 5)
e_prev = 0
t_prev = time.time()
I = 0

def show_image(image):
    plt.imshow(image)
    plt.show()


def is_red_detected(color_sensor):
    """
    Calculates the relative intensity of the red channel compared to
    other channels
    """
    red_ratio_threshold = 1.5
    red, green, blue = color_sensor.rgb()
    print(red, green, blue)
    red_intensity = red / (green + blue)

    return red_intensity > red_ratio_threshold


def is_blue_detected(color_sensor):
    """
       Calculates the relative intensity of the blue channel compared to
       other channels
       """
    blue_ratio_threshold = 1.5
    red, green, blue = color_sensor.rgb()
    blue_intensity = blue / (red + green)

    return blue_intensity > blue_ratio_threshold


def follow_line(color_sensor, left_motor, right_motor):
    """
    An improved line follower algorithm with integral control and deadband.
    """
    color_sensor.image = color_sensor._get_image_sensor()

    reflection = color_sensor.reflection()
    #print("Reflection: {}".format(reflection))

    threshold = 40  # Midpoint between black and white

    Kp = 0.04
    Ki = 0.05
    Kd = 0.005
    MAX_INTEGRAL = 50
    CONST_SPEED = 2

    global e_prev
    global t_prev
    global I

    t = time.time()
    dt = t - t_prev

    # PID calculations
    e = threshold - reflection

    P = e
    D = (e - e_prev) / dt if dt > 0 else 0
    I += e * dt
    
    I = max(min(I, MAX_INTEGRAL), -MAX_INTEGRAL)
    

    if abs(e) < 40:
        P = 0
    
    print(e)

    
    MV = Kp * P + Ki * I + Kd * D

    e_prev = e
    t_prev = t

    right_speed = CONST_SPEED - MV
    left_speed = CONST_SPEED + MV

    # Limit motor speeds to a safe range
    # right_speed = max(min(right_speed, 5), -5)
    # left_speed = max(min(left_speed, 5), -5)
    right_motor.run(speed=right_speed)
    left_motor.run(speed=left_speed)
    

# MAIN CONTROL LOOP
if clientID != -1:

    print('Connected')

    left_motor = Motor(motor_port='A', direction=Direction.CLOCKWISE, clientID=clientID)
    right_motor = Motor(motor_port='B', direction=Direction.CLOCKWISE, clientID=clientID)
    color_sensor = ColorSensor(clientID=clientID)

    while True:
        # End connection

        follow_line(color_sensor, left_motor, right_motor)

else:
    print('Failed connecting to remote API server')
print('Program ended')

# MAIN CONTROL LOOP
