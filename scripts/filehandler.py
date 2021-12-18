from abc import abstractmethod
import subprocess
import cv2 as cv
import os

class MapTypes:
    CLEAN = "clean"
    NORMAL = "normal"
    PATH = "path"

class File_Handler:

    # TODO: Apply Singleton Pattern - safe all opened images in one file
    # @abstractmethod
    # def get_file_loader():
        

    @staticmethod
    def load_map(map, maptype):

        mapdir = 'maps/' + str(map) + '/' + str(maptype) + '.png'
        map = cv.imread(mapdir)

        return map

    @staticmethod
    def get_maps():
        return next(os.walk('maps/.'))[1]
    
    @staticmethod
    def get_paths(map):
        paths = [f for f in os.listdir('maps/'+ map +'/paths/') if f.endswith('.txt')]
        ps = []
        for p in paths:
            ps.append(p.replace('.txt', ''))
        return ps


    @staticmethod
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

    @staticmethod
    def save_path(map, pathname, points, connections):

        path = 'maps/' + map + '/paths/' + pathname + '.txt'

        with open(path, 'w') as f:
            for point in points:
                x = str(round(point[0]))
                y = str(round(point[1]))
                f.write(x + ',' + y + ' ')

            f.write("\n")

            for connection, distance in connections:
                x1 =  str(round(connection[0][0]))
                y1 =  str(round(connection[0][1]))
                x2 =  str(round(connection[1][0]))
                y2 =  str(round(connection[1][1]))
                # sdistance = str(round(self.get_distance(connection[0], connection[1])))
                sdistance = str(round( distance ))
                f.write(x1 + ',' + y1 + '-' + x2 + ',' + y2  + ':' + sdistance + ' ')
            
            print('Path saved')

    @staticmethod
    def load_image(name):

        imagedir = 'images/' + name + '.png'
        image = cv.imread(imagedir)
        
        return image

    @staticmethod
    def load_icon(name):

        icondir = 'images/icons/' + name + '.bmp'
        icon = cv.imread(icondir)
        
        return icon

    @staticmethod
    def load_cascade(name) -> cv.CascadeClassifier:

        cascadedir = 'cascade/' + name + '.xml'
        cascade = cv.CascadeClassifier(cascadedir)
        
        return cascade

    @staticmethod
    def save_image(name, image):

        imagedir = 'debug/' + name + '.png'
        image = cv.imwrite(imagedir, image)

    @staticmethod
    def run_ahk(name):
        filedir = 'ahk/' + name + '.exe'
        subprocess.run([filedir])