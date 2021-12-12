from time import time, sleep
import cv2 as cv
from threading import Thread, Lock
import os
import numpy as np
import math

from numpy import array
from window_capture import WindowCapture
from controller import Controller
from object import Object

class Detection:

    
    MOVEMENT_STOPPED_THRESHOLD = .95
    ORE_CLICKED_THRESHOLD = .80

    stopped = True
    lock = None
    rectangles = []
    movement_screenshot = None
    img_pickaxe = None
    img_ore_clicked = None
    img_mining = None

    minimap_x = 0
    minimap_y = 0
    minimap_width = 150
    minimap_height = 137
    map_x = 0
    map_y = 0
    map_width = 512
    map_height = 512

    last_position = (0,0)

    map = None

    cascade : cv.CascadeClassifier

    wincap: WindowCapture
    controller : Controller

    def __init__(self, model_file_path, wincap, controller) -> None:
        self.lock = Lock()
        self.cascade = cv.CascadeClassifier(model_file_path)

        self.wincap = wincap
        self.controller = controller

        self.img_ore_clicked = cv.imread('ore_clicked.png')
        self.img_mining = cv.imread('mining_bar.png')
        self.img_pickaxe = cv.imread('pickaxe.bmp')

    def get_rectangles(self):
        self.lock.acquire()
        rectangles = self.rectangles
        self.lock.release()
        return rectangles

    def detect_rectangles(self, screenshot):
        return self.cascade.detectMultiScale(screenshot)

    def confirm_hovering_ore(self,x,y):
        
        self.controller.mouse_move(x=x, y=y)
        sleep(.1)
        img = self.wincap.get_cursor_image()
        
        if not img is None:
            result = cv.matchTemplate(img,
                                    self.img_pickaxe,
                                    cv.TM_CCORR_NORMED)
            (min_Val, max_val, min_loc, max_loc) = cv.minMaxLoc(result)
            return max_val == 1
        else:
            return False


    def confirm_mining(self):
        screenshot = self.wincap.make_screenshot()
        #maybe need croping 
        # screenshot = screenshot[746:765, 907:912]
        result = cv.matchTemplate(screenshot[700:900, 900:920],
                                  self.img_mining,
                                  cv.TM_CCORR_NORMED)
        (min_Val, max_val, min_loc, max_loc) = cv.minMaxLoc(result)
        if max_val >= self.ORE_CLICKED_THRESHOLD:
            return True
        return False

    def get_ores(self) -> array: 
        screenshot = self.wincap.make_screenshot()
        rectangles = self.detect_rectangles(screenshot)
        ores = []
        for rectangle in rectangles:

            click_point = self.get_click_points(rectangle = rectangle)
            point = click_point[0]

            if (self.confirm_hovering_ore(point[0], point[1])):
                ores.append(rectangle)
            else:
                # subimg = screenshot[rectangle[1]:rectangle[1] + rectangle[3], rectangle[0]:rectangle[0] + rectangle[2] ]
                # path = 'C:/Users/Josel/OneDrive/Desktop/python/fiesta autominer/wrong'
                # cv.imwrite(os.path.join(path , str(time()) + '.png'), subimg)
                pass
        if len(ores) != 0:
            # path = 'C:/Users/Josel/OneDrive/Desktop/python/fiesta autominer/right'
            # cv.imwrite(os.path.join(path , str(time()) + '.png'), screenshot)
            pass

        return ores


    def get_click_points(self, rectangles = None, rectangle = (0,0,0,0)):
        points = []
        if rectangles == None:
            rectangles = []
        if rectangle[3] != 0:
            rectangles.append(rectangle)

        # Loop over all the rectangles
        for (x, y, w, h) in rectangles:
            # Determine the center position
            center_x = x + int(w/2)
            center_y = y + int(h/2)

            points.append((center_x, center_y))

        return points
    
    def has_stopped_moving(self):
        # if we haven't stored a screenshot to compare to, do that first
        new_screenshot = self.get_minimap()

        if self.movement_screenshot is None:
            self.movement_screenshot = new_screenshot
            return False
        print('Checking stand')
        #check multiple squares whether one stazs the same
        result = cv.matchTemplate(new_screenshot, self.movement_screenshot, cv.TM_CCOEFF_NORMED)
        _minVal, similarity, _minLoc, _maxLoc = cv.minMaxLoc(result, None)
        if similarity == .99:
            return True

        self.movement_screenshot = new_screenshot
        return False
    
    def get_health(self):
        screenshot = self.wincap.make_screenshot()

        #get screenpart with hp bar
        #187 38 
        #276 38
        hb = screenshot
        h = 30 -1
        test = screenshot[h-5:h+5, 186:276]
        cv.imshow('test', test)
        cv.waitKey()
        
        #not bgr 2 2 85
        #is bgr 0 94 244
        health = 0
        #TODO control color
        for x in range(89):   
            print( str(hb[h, x, 0]) + ' ' + str(hb[h, x, 1]) + ' ' + str(hb[h, x, 2])) 
            if str(hb[h, x, 0]) == 0 and str(hb[h, x, 1]) == 94 and str(hb[h, x, 2]) == 244:
                health += 1
        
        #return health %
        return health / 88
    
    def get_minimap(self):
        if self.minimap_x == 0 or self.minimap_y == 0:
            self.get_minimap_position()
        
        screenshot = self.wincap.make_screenshot()
        minimap = screenshot[self.minimap_y : self.minimap_y + self.minimap_height, self.minimap_x : self.minimap_x + self.minimap_width]

        return minimap

    def get_map(self):
        
        #open map
        self.controller.press_key('tab', .2)

        if self.map_x == 0 or self.map_y == 0:
            #if map has not yet been located, get position
            self.get_map_position(True)

        screenshot = self.wincap.make_screenshot()
        
        #close map
        self.controller.press_key('tab', .2)

        map = screenshot[self.map_y : self.map_y + self.map_height, self.map_x : self.map_x + self.map_width]
        return map

    def get_minimap_position(self):
        minimap_symbol = cv.imread('minimap_symbol.png')
        screenshot = self.wincap.make_screenshot()
        result = cv.matchTemplate(screenshot, minimap_symbol, cv.TM_CCOEFF_NORMED)
        _minVal, similarity, _minLoc, maxLoc = cv.minMaxLoc(result, None)

        if similarity > .90:
            self.minimap_x = maxLoc[0] + 3
            self.minimap_y = maxLoc[1] + 17
            return
        else:
            print('Minimap not found')

    def get_map_position(self, map_is_open = False):
        #load map symbol
        map_symbol = cv.imread('map_symbol.png')

        #open map take screenshot and close map
        if  not map_is_open:
            self.controller.press_key('tab', .2)
        screenshot = self.wincap.make_screenshot()
        if  not map_is_open:
            self.controller.press_key('tab', .2)


        result = cv.matchTemplate(screenshot, map_symbol, cv.TM_CCOEFF_NORMED)
        _minVal, similarity, _minLoc, maxLoc = cv.minMaxLoc(result, None)

        if similarity > .95:
            self.map_x = maxLoc[0] - 32
            self.map_y = maxLoc[1] - 1
            return
        else:
            print('Map not found')
    
    def get_player_position(self):
        #get minimap
        minimap = self.get_minimap()

        #load map
        map = cv.imread("maps/goldene_hoehle.png")

        #scale minimap down
        new_size  = (round(self.minimap_width * .31415), round(self.minimap_height * .42))
        new_minimap = cv.resize(minimap, new_size)

        #find closest match
        result = cv.matchTemplate(map, new_minimap, cv.TM_CCOEFF_NORMED)
        _minVal, similarity, _minLoc, maxLoc = cv.minMaxLoc(result, None)

        #get position
        position = (maxLoc[0] + int(72*.31), maxLoc[1] + int(61*.42))
        # print(similarity)

        #if no good hit, search with map
        if similarity < .70:
            
            # get map
            map = self.get_map()

            # load map with no arrow
            empty_map = cv.imread('maps/goldene_hoehle_map.png')

            #get only the different pixels
            difference = cv.subtract(map, empty_map)

            mask = self.extract_color_of_image(difference)

            posx = 0
            posy = 0
            n = 0
            for x in range(500):
                for y in range(500):
                    if mask[y,x] != 0:
                        posx += x
                        posy += y
                        n += 1
            if n != 0:
                posx = posx / n
                posy = posy / n

            
            # mask = cv.drawMarker(mask, (int(posx), int(posy)), (255,0,0))
            # cv.imshow(' ', mask)
            # cv.waitKey()

            position = (int(posx), int(posy))

        #get rotation
        # minimap
        center = (72.5,61.5)
        size = 20.5
        colorrange = ((150,0,0), (240,255,255))
        y1 = int(center[1]-size)
        y2 = int(center[1]+size)
        x1 = int(center[0]-size)
        x2 = int(center[0]+size)
        img = minimap[y1:y2, x1:x2]

        mask = self.extract_color_of_image(img, colorrange)

        posx = 0
        posy = 0
        n = 0

        for x in range(int(2*size)):
                for y in range(int(2*size)):
                    if mask[y,x] != 0:
                        posx += x
                        posy += y
                        n += 1
        if n != 0:
            posx = posx / n
            posy = posy / n
        
        posx -= size
        posy -= size

        angle = math.atan2(posy, posx)
        # angle = math.degrees(math.atan2(posx/posy))

        return Object(position, "Player", angle)

    def extract_color_of_image(self, img, colorrange = ((1,1,1), (255,255,255))):
        #color of arrow
        lower = colorrange[0]
        upper = colorrange[1]

        #find arrow on map
        # create NumPy arrays from the boundaries
        lower = np.array(lower, dtype = "uint8")
        upper = np.array(upper, dtype = "uint8")
        # find the colors within the specified boundaries and apply
        # the mask
        mask = cv.inRange(src=img, lowerb=lower, upperb=upper)

        return mask




