#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait
from pybricks.robotics import DriveBase
import time
e_prev = 0
t_prev = time.time()

e_prev = 0
t_prev = time.time()
I = 0

def follow_line(color_sensor, robot):

    reflection = color_sensor.reflection()

    BLACK = 2
    WHITE = 40
    threshold = (BLACK + WHITE) / 2  # Midpoint between black and white
    global e_prev



    Kp = 7.6   # 7.6
    Kd = 40000 # 400
    Ki = 8   # 0
    MAX_INTEGRAL = 30
    CONST_SPEED = 130

    global e_prev
    global t_prev
    global I



    print(reflection)
    t = time.time()
    dt = t - t_prev
    # PID calculations
    e = reflection - threshold
        
    P = e
    D = e - e_prev
    I += e * dt
    
    I = max(min(I, MAX_INTEGRAL), -MAX_INTEGRAL)


    if abs(I) == MAX_INTEGRAL:
          print("I is maxed out")


    if abs(e) < 19:
        I = 0

    MV = P*Kp + D*Kd + I*Ki
        
    e_prev = e
    t_prev = t

    robot.drive(CONST_SPEED, MV)

# Initialize the motors.
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
color_sensor = ColorSensor(Port.S3)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)


while True:
        follow_line(color_sensor, robot)