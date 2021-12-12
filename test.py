from time import sleep, time
import cv2 as cv
import pyautogui
from datetime import datetime
from threading import Thread, Lock
import win32api, win32con
import math
import os

from math import atan2, cos, sin, sqrt, pi
import numpy as np
from controller import Controller
from detection import Detection
from window_capture import WindowCapture
from object import Object
from bot import Bot
# cd C:\Users\Josel\OneDrive\Desktop\python\fiesta_autominer\
# python test.py

def cd(sec):
    while sec > 0:
        print(sec)
        sleep(1)
        sec -= 1
    
    print('go')

def calc_angle(point1, point2):
    angle = math.atan2(point2[1] - point1[1], (point2[0]- point1[0]))
    return angle

def calc_distance(point1, point2):
    distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    return distance

cd(3)

# set dir to file dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PLAYER_STANDARD_SPEED = 2.55
player_speed = 1.075
player_speed += 2.8
player_speed_count = 1

angle_error = -.091
angle_error_count = 1

wincap = WindowCapture('FiestaOnline')
control =  Controller(0, 0) 
detector = Detection('cascade/cascade.xml', wincap, control)

# walk, in order to let minimapindicator show in same dir as cam
control.press_key('w', .05)

# get destination
destinations = Bot.read_path('maps/exit_path.txt')
# destinations = Bot.read_path('maps/entry_path.txt')

# get position
player = detector.get_player_position()

actual_path = []

start_time = time()

for destination in destinations:

    # calculate distance
    distance = math.sqrt((destination[0] - player.position[0])**2 + (destination[1] - player.position[1])**2)
    print("Distance: " + str(distance))

    ####
    # map = detector.get_map()

    # map = cv.drawMarker(map, player.position, (0,255,255))
    # map = cv.drawMarker(map, destination, (0,0,255))
    # cv.imshow('map', map)
    # cv.waitKey()
    ####

    while distance > 2:
        # safe position for error calculation
        previous_position = player.position

        # calculate angle of destination
        destination_angle = calc_angle(player.position, destination)

        # get turn angle
        turn = destination_angle - player.angle + (angle_error/angle_error_count)
        print('turn: ' + str(math.degrees(turn)))

        # turn camera
        control.turn_camera(turn, total_steps=20)

        #disable failsafe
        pyautogui.FAILSAFE = False  

        # walk for calculated distance
        moving_time = distance / (PLAYER_STANDARD_SPEED * (player_speed / player_speed_count))
        control.press_key('w', moving_time)

        # get position again
        player = detector.get_player_position()

        actual_path.append(player.position)

        # calculate error if distance was bigger then 10
        if distance > 10:
            # get wrong calculations of angle and speed
            actual_angle = calc_angle(previous_position, player.position)
            actual_distance = calc_distance(previous_position, player.position)

            #calc difference
            actual_speed = actual_distance / (moving_time * PLAYER_STANDARD_SPEED)
            print('Speed error: '+ str(actual_speed - (player_speed / player_speed_count)))

            if actual_speed / (player_speed / player_speed_count) > 2/4:
                player_speed += actual_speed
                player_speed_count += 1
            else:
                print('Probably stuck. Actual Speed:' + str(actual_speed) + ' Predicted: ' + str(player_speed / player_speed_count))

            # normalize angle diefference
            angle_difference = destination_angle - actual_angle + (angle_error/angle_error_count)

            if angle_difference > math.radians(180):
                angle_difference -= 2 * math.radians(180)
            
            print('Angle error: '+ str(math.degrees(angle_difference - (angle_error/angle_error_count))))

            if abs(angle_difference) < math.radians(10):
                print('anglediff: ' + str(angle_difference))
                angle_error += angle_difference
                angle_error_count += 1

        # calcularte distance once more
        distance = calc_distance(player.position, destination)
        print("Distance: " + str(distance))

print('Time needed: ' + str(time()- start_time) + ' s')
print('Angle error: '+ str(angle_error/angle_error_count))
print('Speed error: '+ str(player_speed/player_speed_count))

##################################################
# map = cv.imread("maps/goldene_hoehle.png")
map = detector.get_map()

last_destination = destinations[0]
n = 0
for destination in destinations:
    n += 1
    map= cv.drawMarker(map, destination, (255,0,0))
    map = cv.line(map, last_destination, destination, (255,0,0))
    map = cv.putText(map, str(n), destination, cv.FONT_HERSHEY_SIMPLEX, .5, (255,0,255))
    last_destination = destination

last_destination = actual_path[0]
for destination in actual_path:
    map = cv.line(map, last_destination, destination, (0,255,0))
    last_destination = destination
cv.imshow('map', map)
cv.imwrite('path.png', map)
cv.waitKey()


##################################################

# exit

# speedtest
# position, angle = detector.get_player_position()
# control.press_key('w', 10)
# destination, angle = detector.get_player_position()

# distance = math.sqrt((destination[0] - position[0])**2 + (destination[1] - position[1])**2)
# print("Distance: " + str(distance))

# center for minimap
# for n in range(8):
#     control.turn_camera(2*math.pi / 8)
#     control.press_key('w', .01)
#     minimap = detector.get_minimap()
#     name = "mini"+str(n)+".png"
#     cv.imwrite(name, minimap)