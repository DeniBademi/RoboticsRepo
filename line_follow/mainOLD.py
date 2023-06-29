#!/usr/bin/env pybricks-micropython
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait
from pybricks.robotics import DriveBase
import time
e_prev = 0
t_prev = time.time()



def follow_line(color_sensor, robot):

    reflection = color_sensor.reflection()

    BLACK = 2
    WHITE = 35
    threshold = (BLACK + WHITE) / 2  # Midpoint between black and white
    global e_prev

    Kp = 7.6
    Kd = 300

    print(reflection)
    t = time.time()
    # PID calculations
    e = reflection - threshold
        
    P = e
    D = e - e_prev
        
    MV = P*Kp + D*Kd
        
    e_prev = e

    robot.drive(100, MV)

# Initialize the motors.
left_motor = Motor(Port.B)
right_motor = Motor(Port.C)
color_sensor = ColorSensor(Port.S3)
robot = DriveBase(left_motor, right_motor, wheel_diameter=55.5, axle_track=104)


while True:
        follow_line(color_sensor, robot)