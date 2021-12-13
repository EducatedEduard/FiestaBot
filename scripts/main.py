import cv2 as cv
import numpy as np
import os
from pathlib import Path

from pyautogui import sleep
from window_capture import WindowCapture
from detection import Detection
from time import time
from threading import Thread, ThreadError
from bot import Bot, BotState
from timeinfo import TimeInfo

# train cascadet
# D:\OpenCV\opencv\build\x64\vc15\bin\opencv_traincascade.exe -data cascade/ -vec pos.vec -bg neg.txt -w 24 -h 24 -numPos 250 -numNeg 200 -numStages 20 -maxFalseAlarmRate 0.3 -minHitRate 0.999

DEBUG = True
window_name = 'FiestaOnline'

os.chdir(Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute())

bot = Bot(window_name, DEBUG)
ti = TimeInfo()
# sleep(5)
bot.start()
ti.start()

# loop_time = time()
input("Press Enter to continue...")
bot.stop()
ti.stop()

sleep(1)
print ('Done.')
