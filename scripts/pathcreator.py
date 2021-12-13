from tkinter import *
from pathlib import Path
import os#
import math


def load_path(path, scale = 1):
    lines = ()

    points = []
    connections = []

    with open(path) as f:
        lines = f.readlines()

    if len(lines) != 0:
            if lines[0] != "":
                spoints = lines[0].split()
                for s in spoints:
                    scords = s.split(',')
                    x = int(scords[0]) * scale
                    y = int(scords[1]) * scale
                    points.append((x,y))
    if len(lines) > 1:
        if lines[1] != "":
            sconnections = lines[1].split()
            for sconnection in sconnections:
                spoints = sconnection.split('-')
                scords = spoints[0].split(',')
                x = int(scords[0]) * scale
                y = int(scords[1]) * scale
                p1 = (x,y)
                scords = spoints[1].split(',')
                x = int(scords[0]) * scale
                y = int(scords[1]) * scale
                p2 = (x,y)
                connections.append((p1,p2))

    return points, connections

# save path in files
def save_path():
    global points
    global connections
    global selected_point
    global scale
    with open('net.txt', 'w') as f:
        for point in points:
            x = str(round(point[0] / scale))
            y = str(round(point[1] / scale))
            f.write(x + ',' + y + ' ')
        f.write("\n")
        for connection in connections:
            x1 =  str(round(connection[0][0] / scale))
            y1 =  str(round(connection[0][1] / scale))
            x2 =  str(round(connection[1][0] / scale))
            y2 =  str(round(connection[1][1] / scale))
            f.write(x1 + ',' + y1 + '-' + x2 + ',' + y2  + ' ')

# return closest point to x,y
def get_closest_point(x,y):
    global points
    global connections
    global selected_point

    distance = 1000000
    closest_point = (-1,-1)

    for point in points:
        new_distance = math.sqrt((point[0]-x)**2 + (point[1]-y)**2)
        if new_distance < distance:
            distance = new_distance
            closest_point = point
    return closest_point, distance

# draw point 
def draw_point(point, selected = False):
    
    color = "#47A942"
    if selected:
        color = "#DD0000"

    x1, y1 = ( point[0] - 5 ), ( point[1] - 5 )
    x2, y2 = ( point[0] + 5 ), ( point[1] + 5 )
    canvas.create_oval( x1, y1, x2, y2, fill = color )

# draw line
def draw_line(p1, p2):
    canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill='green', width=3)

def left_click(event):
    # add point and create connections
    global points
    global connections
    global selected_point

    x = event.x
    y = event.y
    click_point = (x,y)

    # get closest point
    closest_point, distance = get_closest_point(x,y)

    # if a point is selected and close to another point connect them
    if distance < 10 and selected_point != (-1,-1) and selected_point != closest_point:
        connections.append((selected_point, closest_point))
        draw_line(selected_point, closest_point)
        print('Connection added: (' + str(selected_point) + ',' + str(closest_point) + ')')
        draw_point(closest_point, True)
        draw_point(selected_point)
        selected_point = closest_point
    else:
        # add point
        print('Point added: (' + str(x) + ',' + str(y) + ')')
        points.append(click_point)
        draw_point(click_point)

    
def right_click(event):
    # select point
    global points
    global connections
    global selected_point
    
    # get closest point
    closest_point, distance = get_closest_point(event.x,event.y)

    # select
    if distance < 10:
        draw_point(selected_point)
        selected_point = closest_point
        draw_point(selected_point, True)
    else:
        print('No point near')

def middle_click(event):
    # delete point
    global points
    global connections
    global selected_point

    # get closest point
    closest_point, distance = get_closest_point(event.x,event.y)

    # delete
    if distance < 10:
        if selected_point == closest_point:
            selected_point = (-1,-1)
        # remove from points
        points.remove(closest_point)

        # remove from connections
        remove = []
        for p1, p2 in connections:
            if p1 == closest_point or p2 == closest_point:
                remove.append((p1,p2))
        
        connections = [connection for connection in connections if connection not in remove]

        #redraw
        redraw()

    else:
        print('No point near')

def redraw():
    global points
    global connections
    global selected_point
    global canvas
    global img

    canvas.create_image(0,0, anchor=NW, image=img)
    canvas.pack(expand = YES, fill = BOTH)
    for connection in connections:
        draw_line(connection[0], connection[1])
    for point in points:
        draw_point(point)

# save path when window is closed
def close_window():
    global canvas
    print('Window closed')
    save_path()
    master.destroy()

image_width = 500
image_height = 500

scale = 2

canvas_width = 500 * scale
canvas_height = 500 * scale
points = []
connections = []
selected_point = (-1,-1)

# set dir to parent dir of this dir
os.chdir(Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute())

master = Tk()
master.protocol("WM_DELETE_WINDOW", close_window)
master.title( "Draw route" )
canvas = Canvas(master, 
           width=canvas_width, 
           height=canvas_height)

img = PhotoImage(file="maps/goldene_hoehle/clean.png")
img = img.zoom(scale, scale)

canvas.create_image(0,0, anchor=NW, image=img)

canvas.pack(expand = YES, fill = BOTH)
canvas.bind( "<Button-3>", right_click )
canvas.bind( "<Button-2>", middle_click )
canvas.bind( "<Button-1>", left_click )
# message = Label( master, text = "Press and Drag the mouse to draw" )
# message.pack( side = BOTTOM )

# load netfile
points, connections = load_path('net.txt', scale)

# draw them
redraw()
    
mainloop()

