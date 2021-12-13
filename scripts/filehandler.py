from abc import abstractmethod
import subprocess
import cv2 as cv
from numpy import string_

class MapTypes:
    CLEAN = "clean"
    NORMAL = "normal"
    PATH = "path"


class File_Handler:

    # TODO: Apply Singleton Pattern - safe all opened images in one file
    # @abstractmethod
    # def get_file_loader():
        

    @abstractmethod
    def load_map(map, maptype):

        mapdir = 'maps/' + str(map) + '/' + str(maptype) + '.png'
        map = cv.imread(mapdir)

        return map

    @abstractmethod
    def load_path(map, pathname):
        path = 'maps/' + map + '/paths/' + pathname + '.txt'
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

    @abstractmethod
    def load_image(name):

        imagedir = 'images/' + name + '.png'
        image = cv.imread(imagedir)
        
        return image

    @abstractmethod
    def load_icon(name):

        icondir = 'images/icons/' + name + '.bmp'
        icon = cv.imread(icondir)
        
        return icon

    @abstractmethod
    def load_cascade(name) -> cv.CascadeClassifier:

        cascadedir = 'cascade/' + name + '.xml'
        cascade = cv.CascadeClassifier(cascadedir)
        
        return cascade

    @abstractmethod
    def save_image(name, image):

        imagedir = 'debug/' + name + '.png'
        image = cv.imwrite(imagedir, image)

    @abstractmethod
    def run_ahk(name):
        filedir = 'ahk/' + name + '.exe'
        subprocess.run([filedir])