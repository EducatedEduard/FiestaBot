import pydirectinput
import pyautogui
from time import sleep
from threading import Thread, Lock
import win32api
import win32con
import math

from filehandler import File_Handler

class Controller:

    stopped = True
    lock = None

    ACTION_CLICK = 1
    ACTION_PRESS_KEY = 2
    ACTION_WRITE = 3

    DELAY_CLICK = .2
    DELAY_PRESS = .05
    DELAY = 0

    FULLTURN = 1028.572

    #screen 80 Grad auf 45 Grad

    offset_x = 0
    offset_y = 0

    def __init__(self, offset_x, offset_y) -> None:
        self.lock = Lock()
        self.offset_x = offset_x
        self.offset_y = offset_y

        pyautogui.FAILSAFE = False

    def click(self,x=None,y=None):
        # self.__queueAction((self.ACTION_CLICK, x, y))
        self.__click(x,y)
    def press_key(self, key, duration = -1 ):
        if duration == -1:
            duration = self.DELAY_PRESS
        #https://pyautogui.readthedocs.io/en/latest/keyboard.html#keyboard-keys
        self.__press_key(key, duration)
        # self.__queueAction((self.ACTION_PRESS_KEY,key))
    def write(self, text):
        self.__write(text)
        # self.__queueAction((self.ACTION_WRITE, text))

    def mouse_move(self, x, y):
        x,y = self.convert_to_screen(x,y)
        pyautogui.moveTo(x,y)#

    def key_down(self, key):
        pydirectinput.keyDown(key)

    def key_up(self, key):
        pydirectinput.keyUp(key)

    def turn_camera(self, xAngle, yAngle=0, total_steps=50):
        #move mouse to midscreen
        x,y = pyautogui.position()
        self.mouse_move(960, 540)

        # dont moe then 1 time and dont turn over 180 degree
        xAngle = xAngle % (2 * math.pi)

        if xAngle > math.pi:
            xAngle = xAngle - 2 * math.pi


        xDistance = self.FULLTURN / (math.pi * 2) * xAngle
        yDistance = self.FULLTURN / (math.pi * 2) * yAngle

        # get steps
        steps = self.__get_steps(xDistance, yDistance, total_steps)

        pyautogui.mouseDown(button='right')
        sleep(self.DELAY_CLICK)
        for (x, y) in steps:
            win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, x, y) 
            sleep(.01)
        pyautogui.mouseUp(button='right')
        sleep(self.DELAY_CLICK)
        self.mouse_move(x, y)

    def activate_mine_script(self):
        File_Handler.run_ahk("mine")
    
    def __click(self, x, y):
        if x != None:
            self.mouse_move(x, y)
        pyautogui.mouseDown()
        sleep(self.DELAY_CLICK)
        pyautogui.mouseUp()

    def __write(self, text):
        pyautogui.write(text)

    def __press_key(self, key, duration):
        self.mouse_move(960,540)
        pydirectinput.keyDown(key)
        sleep(duration)
        pydirectinput.keyUp(key)

    def convert_to_screen(self,x,y):
        x += self.offset_x
        y += self.offset_y
        return (x,y)
    
    def __get_steps(self, x_distance, y_distance, total_steps):
        #1028,572 ist eine umdrehung
        steps = []
        x_distance = round(x_distance)
        y_distance = round(y_distance)

        x_stepsize = round(x_distance / total_steps)
        y_stepsize = round(y_distance / total_steps)
        extra_step = (x_distance - total_steps * x_stepsize, y_distance - total_steps * y_stepsize)

        for _ in range(total_steps):
            steps.append((x_stepsize, y_stepsize))
        
        steps.append(extra_step)

        return steps

    def reset_camera_angle(self):
        self.turn_camera(0, 150/180*2*math.pi, 15)
        self.turn_camera(0, -70/180*2*math.pi, 10)