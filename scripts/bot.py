#!/usr/bin/python
# -*- coding: utf-8 -*-
import enum
from time import time, sleep
from numpy import mod, true_divide
import pyautogui
from threading import Thread, Lock
import cv2 as cv
from enum import Enum

from win32con import DIFFERENCE
from controller import Controller
from detection import Detection
from window_capture import WindowCapture
from PIL import Image
import math
import random
from object import Object

class BotState:

    INITIALIZING = 'Initializing'
    SEARCHING = 'Searching'
    MOVING = 'Moving'
    APPROUCH = 'Approuching'
    MINING = 'Mining'
    PICKUP = 'Picking up'
    ATTACK = 'Attacking'

class Bot:

    INITIALIZING_SECONDS = 1
    MINING_SECONDS = 5
    POV = 80

    ORE_SIZE = (.84, .69)

    stopped = True
    lock = None

    state = None
    path = []
    # targets = []
    # screenshot = None
    timestamp = None
    movement_screenshot = None
    ores_mined = 0

    DEBUG = False

    detector = None
    wincap = None
    control = None

    def __init__(self, window_name, DEBUG = True):
        self.DEBUG = DEBUG

        self.lock = Lock()

        print('starte threads:')
        self.set_state(BotState.INITIALIZING)
        self.timestamp = time()

        self.wincap = WindowCapture(window_name)
        self.control = Controller(self.wincap.offset_x, self.wincap.offset_y)
        self.detector = Detection('cascade/cascade.xml', self.wincap, self.control)

        self.path = self.read_path('maps/path.txt')



    def start(self):
        # self.wincap.start()
        # self.detector.start()
        # self.control.start()
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True
        # self.detector.stop()
        # self.control.stop()

    def run(self):
        while not self.stopped:
            
            #heal if health is below 50 
            #TODO
            # if self.detector.get_health() < 50:
            #     self.set_state(BotState.ATTACK)

            self.wincap.make_screenshot()
            if self.state == BotState.INITIALIZING:
                if time() > self.timestamp + self.INITIALIZING_SECONDS:
                    sleep(5)
                    self.detector.get_map_position( )

                    self.set_state(BotState.SEARCHING)

            elif self.state == BotState.SEARCHING:
                # get new ores
                ores = self.detector.get_ores()
                
                if len(ores) > 0:
                    #sort ores
                    self.sort_targets(ores)
                    ore = ores[0]
                    
                    point = self.detector.get_click_points(rectangle=ore)[0]

                    #click first ore
                    self.control.click(x = point[0], y = point[1])
                    sleep(0.1)     
                    self.control.click()

                    #turn camera to ore
                    vo, av = self.calc_position(ore, self.ORE_SIZE)
                    vp = 10
                    
                    #calc turn angle
                    op = math.sqrt(vp**2 + vo**2 - 2 * vp * vo * math.cos(av))

                    angle_person = 0
                    if op > vp:
                        angle_ore = math.asin(math.sin(av)/op * vp)
                        angle_person = math.pi - av - angle_ore
                    else :
                        #TODO fix vo > op
                        angle_person = math.asin(math.sin(av)/op * vo)
                        angle_ore = math.pi - av - angle_person

                    angle_turn = math.pi - angle_person
                    self.control.turn_camera(angle_turn, 0, 1)

                    self.set_state(BotState.APPROUCH)
                    continue
                    
                self.set_state(BotState.MOVING)

            elif self.state == BotState.APPROUCH:
                start = time()

                #wait till mining has started
                while (not self.stopped):

                    #if target is not reached after 30 sec, go back searching
                    if time() - start > 30:
                        self.set_state(BotState.SEARCHING)
                        break
                    
                    #if started mining go mining state
                    if self.detector.confirm_mining():

                        self.set_state(BotState.MINING)
                        break
                
               
            elif self.state == BotState.MOVING:
                #move until either ores are found or wall is hit

                #after 30 secs of moving randomly turn
                start = time()
                turn = False

                while(not self.stopped):

                    #every 30 secs randomly turn
                    if (time() - start) % 30 > 20 and turn == True:
                        turn = False
                        angle = random.random() * 2 * math.pi - math.pi
                        self.control.turn_camera(angle)
                    else:
                        turn = True

                    #walk staight
                    self.control.key_down('w')
                    sleep(1)
                    self.control.key_up('w')
                    #check wether an ore is found
                    ores = self.detector.get_ores()
                    #if an ore was hovered, go to searching state
                    if len(ores) > 0:
                        self.state = BotState.SEARCHING
                        break

                    #check wether bot stopped moving
                    if self.detector.has_stopped_moving():
                        #turn around
                        # print('hit wall')
                        self.control.turn_camera(1)

            elif self.state == BotState.MINING:
                
                #start mine script
                self.control.activate_mine_script()

                #TODO click bar...
                while self.detector.confirm_mining() and not self.stopped:
                    pass

                self.set_state(BotState.PICKUP)

            elif self.state == BotState.PICKUP:
                #TODO: pick up every dropped item by moving in every direction a little bit
                self.control.press_key('x')
                self.control.press_key('x')
                self.control.press_key('x')
                self.control.press_key('x')

                self.ores_mined += 1
                print('Ores mined: ' + str(self.ores_mined))
                
                x = 0
                turn_steps = 5
                while x < turn_steps:
                    x += 1
                    ores = self.detector.get_ores()
                    if len(ores) != 0:
                        self.set_state(BotState.SEARCHING)
                        break
                    else:
                        self.control.turn_camera(2 * math.pi / turn_steps)

                self.set_state(BotState.SEARCHING)
            
            elif self.state == BotState.ATTACK:
                #TODO Attack mobs 
                self.control.press_key('3')
                self.set_state(BotState.SEARCHING)

    def sort_targets(self, targets):

        def lowest_y(pos):
            return -pos[1]

        return targets.sort(key=lowest_y)

    def set_state(self, state):
        self.lock.acquire()
        self.state = state
        print(state)
        self.lock.release()
        pass

    def calc_position(self, object, size):
        #object = (start_x. start_y, width, height) : object pixelcoordinates
        #size = (x, y) : object size in m
        av = ((2 * object[0] + object[2]) / 2 - 960) / 1920 * 80

        o_angle = (object[2] / 1920 * 80, object[3] / 1080 * 45)
        vo1 = size[0] / math.tan(o_angle[0])
        vo2 = size[1] / math.tan(o_angle[0])

        # print('calc distance: ' + str(vo1) + ' + ' + str(vo2))
        vo = (vo1 + vo2)/2 
        return vo, av
    
    @staticmethod
    def read_path(path):
        txt = open(path)
        points = []
        line = ""
        for l in txt:
            if l != "":
                line =  l

        cords = line.split()
        for s in cords:
            p = s.split(',')
            points.append((int(p[0]), int(p[1])))

        return points

    def get_distance(self, object : Object, destination):
        self.control.press_key('w', .05)

        dangle = math.atan2(destination[1]- object.position[1], (destination[0]- object.position[0]))

        turn = dangle - object.angle

        distance = math.sqrt((destination[0] - object.position[0])**2 + (destination[1] - object.position[1])**2)

        return distance, turn, object.position


    
