
from abc import abstractmethod
import math
from os import path
from threading import Thread, Lock
from controller import Controller
from detection import Detection
from time import sleep, time
from numpy import *

from object import Object

class CameraController:

    controller : Controller
    lock = None
    stopped = True
    path = None
    wincap = None
    detection : Detection

    angle_error = -.091

    
    def __init__(self, controller, detection, path):
        self.controller = controller
        self.lock = Lock()
        self.path = path
        self.detection = detection
    
    def start(self):
        self.stopped = False
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.stopped = True

    def run(self):
        # set first target
        targetnumber = 0

        # start walking
        start_time = time()
        self.controller.key_down('w')
        
        self.controller.mouse_move(960, 740)
        self.controller.mouse_down('right')

        while not self.stopped and targetnumber < len(self.path):
            # set target
            target = self.path[targetnumber]

            # get position
            # 0.05
            player = self.detection.get_player_position()

            distance = self.calc_distance(player.position, target)
            angle = self.calc_angle(player.position, target)

            # check if target is reached
            if distance < 3:
                print('Reached Target: ' + str(targetnumber))
                targetnumber += 1
                continue

            # get turn angle
            turn = (angle - player.angle + self.angle_error)/(2 + 10/distance)
            # turn = (angle - player.angle + self.angle_error)

            #only turn if not going to hit target
            if self.calc_miss_by(player, target) > 2:
                self.controller.turn_camera(turn, button_is_down=True, stepsize=10)
            # TODO: calculate angle error   

            # TODO: check if stuck
        
        #stop walking
        self.controller.key_up('w')
        self.controller.mouse_up('right')

        print('Time needed: ' + str(time()- start_time) + ' s')

    def calc_angle(self, point1, point2):
        angle = math.atan2(point2[1] - point1[1], (point2[0]- point1[0]))
        return angle

    def calc_distance(self, point1, point2):
        distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
        return distance

    def calc_miss_by(self, line : Object, point):
        # get gradient
        y = math.tan(line.angle)
        x = 1
        p1 = array([line.position[0],line.position[1]])
        p2 = array([line.position[0] + x,line.position[1] + y])

        # get line that crosses with right angle
        x = -y
        y = x

        p3 = array([point[0],point[1]])
        p4 = array([point[0] + x,point[1] + y])

        intersection = self.seg_intersect(p1, p2, p3, p4)

        return self.calc_distance(intersection, p3)

    def seg_intersect(self, a1,a2, b1,b2) :
        def perp( a ) :
            b = empty_like(a)
            b[0] = -a[1]
            b[1] = a[0]
            return b

        da = a2-a1
        db = b2-b1
        dp = a1-b1
        dap = perp(da)
        denom = dot( dap, db)
        num = dot( dap, dp )
        return (num / denom.astype(float))*db + b1