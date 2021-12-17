from tkinter import *
from pathlib import Path
from time import sleep
from pathcreator import PathCreator
import os
import math
from numpy import *

class PathSelector:

    master : Tk
    clickpoint = (0,0)
    stopped = False
    map = ""
    startpoint = (0,0)
    endpoint = (0,0)
    points = ()
    connections = ()
    selected_path = ()
    selected_points = ()
    new_points = ()

    def __init__(self):
        pass

    # @staticmethod
    def calc_path(self, mapname, startpoint, endpoint):

        points = ()
        distance = 0

        # if already at the destination return that point
        if startpoint == endpoint:
            return ((startpoint)), 0

        nodes, connections = PathCreator.load_path("maps/" + mapname + "/paths/net.txt")

        # get closest point to start and end
        closest_to_start = []
        closest_to_end = []
        for point in nodes:
            d_start = self.calc_distance(point, startpoint)
            d_end = self.calc_distance(point, endpoint)
            # if no start/ end is set yet set first
            if closest_to_start == []:
                closest_to_start = (point, d_start)
                closest_to_end = (point, d_end)
            
            # if distance is closer replace
            else:
                if d_start < closest_to_start[1]:
                    closest_to_start = (point, d_start)
                if d_end < closest_to_end[1]:
                    closest_to_end = (point, d_end)

        # start pathfinding from closest points
        start = closest_to_start[0]
        end = closest_to_end[0]

        #TODO: FIX: Some routes are looked twice into

        old_points = []
        new_points = [(start, 0, [start])]
        while (True):
            # self.redraw()
            # get point  
            if len(new_points) > 0:
                
                # sort all points - to get the one with lowest distance
                new_points.sort(key=lambda x: x[1])
                p1, d1, r1 = new_points[0]

                # add point to old list
                old_points.append((p1, d1, r1))

                # if endpoint is reached, stop
                # if p1 == end:
                    # break
            
                # get all connections
                next_points = PathSelector.get_next(connections, p1)

                for p2, d2 in next_points:

                    # if point is already in route, skip  this connection
                    if p2 in r1:
                        continue
                    
                    # add distances and routes to get the new route
                    d2 = d2 + d1
                    r2 = []
                    for r in r1:
                        r2.append(r)    
                    r2.append(p2)

                    # if next point has already been added, check if distance is smaller
                    found = False
                    for p3, d3, r3 in old_points:
                        if p2 == p3:
                            if d2 < d3:
                                new_points.append((p2, d2, r2))
                            found = True
                            break
                    
                    # if not found add
                    if not found:
                        new_points.append((p2, d2, r2))
                
                # point has been searched, remove it from new list
                new_points.remove((p1, d1, r1))
                
                # remove duplicates from new points
                updated_points = []
                for p1, d1, r1 in new_points:
                    add = True
                    for p2, d2, r2 in new_points:
                        # if route with same destination and smaller distance exists dont add
                        if (p1, d1, r1) != (p2, d2, r2):
                            if p1 == p2:
                                if d1 < d2:
                                    add = False
                                    break
                                # if distance is equal, take the one with less points
                                elif d1 == d2:
                                    if len(r1) > len(r2):
                                        add = False
                                    elif len(r1) == len(r2):
                                        # if equal amount of points, only add first
                                            for p3, d3, r3 in updated_points:
                                                if p3 == p1:
                                                    add = False
                                                    break
                                    break
                    # if no better route, add
                    if add:
                        updated_points.append((p1, d1, r1))

                new_points = []
                for p in updated_points:
                    new_points.append(p)

            else:
                # if no new points are found stop
                break
            
        # get end point and return route
        route = []
        route.append(startpoint)
        distance = 0
        for p1, d1, r1 in old_points:
            if p1 == end:
                route += r1
                distance = d1
                break
        route.append(endpoint)

        return route, distance
    
    @staticmethod
    def get_next(connections, point):
        next = []
        for connection, distance in connections:
            if connection[0] == point:
                next.append((connection[1], distance))
            elif connection[1] == point:
                next.append((connection[0], distance))
        return next


    @staticmethod
    def get_distance(point, connection):
        # get gradient
        x = connection[1][0] - connection[0][0]
        y = connection[1][1] - connection[0][1]
        a1 = array([connection[0][0], connection[0][1]])
        a2 = array([connection[1][0], connection[1][1]])

        # get line that crosses with right angle
        x = -y
        y = x

        b1 = array([point[0],point[1]])
        b2 = array([point[0] + x,point[1] + y])

        da = a2-a1
        db = b2-b1
        dp = a1-b1

        # turn 90 degree
        b = empty_like(da)
        b[0] = -da[1]
        b[1] = da[0]

        dap = b
        denom = dot( dap, db)
        num = dot( dap, dp )

        intersection = (num / denom.astype(float))*db + b1

        # check if intersection is on the connection
        n = (connection[0][0] + intersection[0]) / x
        closest = ()

        # point lays between
        if n >= 1 and n <= 0:
            closest = intersection
            distance =  PathSelector.calc_distance(closest, point)

        # point lays outside
        elif n < 0:
            closest = connection[0]
            distance =  PathSelector.calc_distance(closest, point)
        
        else:
            closest = connection[1]
            distance =  PathSelector.calc_distance(closest, point)

        return distance, closest

    @staticmethod
    def calc_distance(point1, point2):
        distance = math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
        return distance
        
    def ui_get_path_end(self, mapname, startpoint):
        self.map = mapname
        self.startpoint = startpoint

        self.clickpoint = (0,0)
        self.scale = 2
        canvas_width = 500
        canvas_height = 500
        self.master = Tk()

        self.master.protocol("WM_DELETE_WINDOW", self.close)
        self.master.title( "Select" )
        self.canvas = Canvas(self.master, 
                width=canvas_width * self.scale, 
                height=canvas_height * self.scale)

        self.img = PhotoImage(file="maps/" + mapname + "/normal.png")
        self.img = self.img.zoom(self.scale, self.scale)

        self.canvas.create_image(0,0, anchor=NW, image=self.img)

        self.canvas.pack(expand = YES, fill = BOTH)
        self.canvas.focus_set()
        self.canvas.bind( "<Button-1>", self.left_click )
        self.canvas.bind( "<Key>", self.key_press )

        self.points, self.connections = PathCreator.load_path("maps/" + mapname + "/paths/net.txt")
        self.master.attributes("-topmost", True)

        self.redraw()

        mainloop()

    def close(self):

        print('Window closed')
        self.master.destroy()

    def left_click(self, event):
        self.endpoint = (round(event.x/self.scale),round(event.y/self.scale))
        self.selected_points, distance = self.calc_path(self.map, self.startpoint, self.endpoint)
        self.redraw()
    
    def key_press(self, event):
        # move point small amounts
        if event.keysym == 'Escape' or event.keysym == 'Return':
            self.close()
    
    # draw point 
    def draw_point(self, point, color):

        x1, y1 = ( point[0] * self.scale - 5 ), ( point[1] * self.scale- 5 )
        x2, y2 = ( point[0] * self.scale+ 5 ), ( point[1] * self.scale+ 5 )
        self.canvas.create_oval( x1, y1, x2, y2, fill = color )
    
    # draw line
    def draw_line(self, p1, p2, selected = False):
                
        color = "#47A942"
        if selected:
            color = "#DD0000"

        self.canvas.create_line(p1[0]* self.scale, p1[1]* self.scale, p2[0]* self.scale, p2[1]* self.scale, fill=color, width=3)

    def redraw(self):
        self.canvas.delete("all")
        self.canvas.create_image(0,0, anchor=NW, image=self.img)
        self.canvas.pack(expand = YES, fill = BOTH)

        # draw all connections
        for connection, distance in self.connections:
            self.draw_line(connection[0], connection[1])

        # draw all points
        for point in self.points:
            self.draw_point(point, "green")

        # draw selected connections
        for connection, distance in self.selected_path:
            self.draw_line(connection[0], connection[1], True)
        
        # draw selected points
        for point in self.selected_points:
            self.draw_point(point, "red")

        # draw points that are being searched
        for point, d, r in self.new_points:
            self.draw_point(point, "Yellow")

        # draw start and endpoint
        self.draw_point(self.startpoint, "Blue")
        if self.endpoint != (0,0):
            self.draw_point(self.endpoint, "Blue")


