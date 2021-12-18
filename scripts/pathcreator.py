from tkinter import *
from pathlib import Path
import os
import math

from filehandler import File_Handler

class PathCreator:

    points = []
    connections = []
    selected_point =None
    scale = 2
    master : Tk
    canvas : Canvas
    img = None
    map = ""
    path = ""

    def __init__(self, map, path):

        self.map = map
        self.path = path

        canvas_width = 500 * self.scale
        canvas_height = 500 * self.scale

        # set dir to parent dir of this dir
        os.chdir(Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute())

        self.master = Tk()
        self.master.protocol("WM_DELETE_WINDOW", self.close_window)
        self.master.title( "Draw route" )
        self.canvas = Canvas(self.master, 
                width=canvas_width, 
                height=canvas_height)

        self.img = PhotoImage(file="maps/" + map + "/normal.png")
        self.img = self.img.zoom(self.scale, self.scale)

        self.canvas.create_image(0,0, anchor=NW, image=self.img)

        self.canvas.pack(expand = YES, fill = BOTH)
        self.canvas.focus_set()
        self.canvas.bind( "<Button-3>", self.right_click )
        self.canvas.bind( "<Button-2>", self.middle_click )
        self.canvas.bind( "<Button-1>", self.left_click )
        self.canvas.bind("<Key>", self.key_press)
        #TODO: Add keylistener, 
        # arrow keys to move points
        # tab to select next

        # # message = Label( master, text = "Press and Drag the mouse to draw" )
        # message.pack( side = BOTTOM )

        # load netfile
        self.points, self.connections = self.load_path('maps/' + map + '/paths/'+ self.path + '.txt')

        # draw them
        self.redraw()
        
        # put to top
        self.master.attributes("-topmost", True)

        mainloop()
    @staticmethod
    def load_path(path):
        lines = ()

        points = []
        connections = []
        try:
            with open(path) as f:
                lines = f.readlines()

            if len(lines) != 0:
                    if lines[0] != "":
                        spoints = lines[0].split()
                        for s in spoints:
                            scords = s.split(',')
                            x = int(scords[0])
                            y = int(scords[1])
                            points.append((x,y))
            if len(lines) > 1:
                if lines[1] != "":
                    sconnections = lines[1].split()
                    for sconnection in sconnections:
                        spointsdistance = sconnection.split(':')
                        distance = int(spointsdistance[1])
                        spoints = spointsdistance[0].split('-')
                        scords = spoints[0].split(',')
                        x = int(scords[0])
                        y = int(scords[1])
                        p1 = (x,y)
                        scords = spoints[1].split(',')
                        x = int(scords[0])
                        y = int(scords[1])
                        p2 = (x,y)
                        connections.append(((p1,p2), distance))
        except FileNotFoundError:
            pass

        return points, connections

    # return closest point to x,y
    def get_closest_point(self, p1):

        distance = 1000000
        closest_point = None

        for p2 in self.points:
            new_distance = self.get_distance(p1, p2)
            if new_distance < distance:
                distance = new_distance
                closest_point = p2
        return closest_point, distance

    def get_distance(self, p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    # draw point 
    def draw_point(self, point, selected = False):
        
        color = "#47A942"
        if selected:
            color = "#DD0000"

        x1, y1 = ( point[0] * self.scale - 5 ), ( point[1] * self.scale  - 5 )
        x2, y2 = ( point[0] * self.scale  + 5 ), ( point[1] * self.scale  + 5 )
        self.canvas.create_oval( x1, y1, x2, y2, fill = color )

    # draw line
    def draw_line(self, p1, p2):
        self.canvas.create_line(p1[0] * self.scale , p1[1] * self.scale , p2[0] * self.scale , p2[1] * self.scale , fill='green', width=3)

    def left_click(self, event):
        # add point and create connections
        click_point = (round(event.x / self.scale), round(event.y / self.scale))

        # get closest point
        closest_point, distance = self.get_closest_point(click_point)

        # if a point is selected and close to another point connect them
        if distance < 30 and self.selected_point !=None and self.selected_point != closest_point:

            #check if connections exists already
            for connection, distance in self.connections:
                if (connection[0] == closest_point and connection[1] == self.selected_point) or (connection[1] == closest_point and connection[0] == self.selected_point):
                    return
            distance = self.get_distance(closest_point, self.selected_point)
            self.connections.append(((self.selected_point, closest_point), round(distance)))
            self.draw_line(self.selected_point, closest_point)
            print('Connection added: (' + str(self.selected_point) + ',' + str(closest_point) + ')')
            self.draw_point(closest_point, True)
            self.draw_point(self.selected_point)
            self.selected_point = closest_point
        else:
            # dont add if points to close
            if distance < 10:
                return
            # add point
            print('Point added: (' + str(click_point[0]) + ',' + str(click_point[1]) + ')')
            self.points.append(click_point)
            self.draw_point(click_point)

        
    def right_click(self, event):
        # select point
        click_point = (round(event.x / self.scale), round(event.y / self.scale))
        
        # get closest point
        closest_point, distance = self.get_closest_point(click_point)

        # select
        if distance < 30:
            if self.selected_point != None:
                self.draw_point(self.selected_point)
            self.selected_point = closest_point
            self.draw_point(self.selected_point, True)
        else:
            print('No point near')

    def middle_click(self, event):
        # delete point
        click_point = (round(event.x / self.scale), round(event.y / self.scale))

        # get closest point
        closest_point, distance = self.get_closest_point(click_point)

        # delete
        if distance < 15:
            # if deleted point is selected, unselect
            if self.selected_point == closest_point:
                self.selected_point =None

            # remove from points
            self.points.remove(closest_point)

            # remove from connections
            keep = []
            for (p1, p2), distance in self.connections:
                if p1 != closest_point and p2 != closest_point:
                    keep.append(((p1,p2), distance))
            
            self.connections = keep
            #redraw
            self.redraw()

        else:
            print('No point near')

    def key_press(self, event):

        # move point small amounts
        if event.keysym == 'Up':
            if self.selected_point !=None:
                self.change_point(self.selected_point, (self.selected_point[0], self.selected_point[1] - 1))
                self.redraw()
        elif event.keysym == 'Down':
            if self.selected_point !=None:
                self.change_point(self.selected_point, (self.selected_point[0], self.selected_point[1] + 1))
                self.redraw()
        elif event.keysym == 'Left':
            if self.selected_point !=None:
                self.change_point(self.selected_point, (self.selected_point[0] - 1, self.selected_point[1]))
                self.redraw()
        elif event.keysym == 'Right':
            if self.selected_point !=None:
                self.change_point(self.selected_point, (self.selected_point[0] + 1, self.selected_point[1]))
                self.redraw()


        elif event.keysym == 'Escape':
            pass
        elif event.keysym == 'Space':
            pass
        elif event.keysym == 'Tab':
            pass
        print(event)

    def redraw(self):
        self.canvas.delete("all")
        self.canvas.create_image(0,0, anchor=NW, image=self.img)
        self.canvas.pack(expand = YES, fill = BOTH)

        # draw all connections
        for connection, distance in self.connections:
            self.draw_line(connection[0], connection[1])

        # draw all points
        for point in self.points:
            if point == self.selected_point:
                self.draw_point(point, True)
            else:
                self.draw_point(point)

    def change_point(self, old, new):
        # change points
        new_points = []
        for p in self.points:
            if old != p:
                new_points.append(p)
        new_points.append(new)

        self.points = new_points

        # change connections
        new_connections = []
        for c, distance in self.connections:
            if old == c[0]:
                new_connections.append(((new, c[1]), distance))
            elif  old == c[1]:
                new_connections.append(((new, c[0]), distance))
            else:
                new_connections.append((c, distance))
        self.connections = new_connections
        self.selected_point = new

    # save path when window is closed
    def close_window(self):
        print('Window closed')
        File_Handler.save_path(self.map, self.path, self.points, self.connections)
        self.master.destroy()

if __name__ == "__main__":
    # set dir to parent dir of this dir
    os.chdir(Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute())

    c = 1

    maps = File_Handler.get_maps()
    for map in maps:
        print(str(c) + ': ' + map)
        c += 1

    # ask for map
    ask = True
    while ask:
        n = int(input('Choose map: ')) - 1
        if n >= 0 and n < len(maps):
            ask = False
    map = maps[n]

    # ask for path
    c = 1
    print('________________________________________')
    paths = File_Handler.get_paths(map)
    paths.append('New Path')

    for path in paths:
        print(str(c) + ': ' + path)
        c += 1

    ask = True
    while ask:
        n = int(input('Choose path: ')) - 1
        if n >= 0 and n < len(paths):
            ask = False

    if n == len(paths) - 1:
        name = input('Path name: ')
    else:
        name = paths[n]

    pc = PathCreator(map, name)