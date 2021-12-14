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
                spointsdistance = sconnection.split(':')
                distance = int(spointsdistance[1])
                spoints = spointsdistance[0].split('-')
                scords = spoints[0].split(',')
                x = int(scords[0]) * scale
                y = int(scords[1]) * scale
                p1 = (x,y)
                scords = spoints[1].split(',')
                x = int(scords[0]) * scale
                y = int(scords[1]) * scale
                p2 = (x,y)
                connections.append(((p1,p2), distance))

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
        for connection, distance in connections:
            x1 =  str(round(connection[0][0] / scale))
            y1 =  str(round(connection[0][1] / scale))
            x2 =  str(round(connection[1][0] / scale))
            y2 =  str(round(connection[1][1] / scale))
            sdistance = str(round( distance / scale ))
            f.write(x1 + ',' + y1 + '-' + x2 + ',' + y2  + ':' + sdistance + ' ')

# return closest point to x,y
def get_closest_point(p1):
    global points
    global selected_point

    distance = 1000000
    closest_point = None

    for p2 in points:
        new_distance = get_distance(p1, p2)
        if new_distance < distance:
            distance = new_distance
            closest_point = p2
    return closest_point, distance

def get_distance(p1, p2):
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

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
    closest_point, distance = get_closest_point(click_point)

    # if a point is selected and close to another point connect them
    if distance < 30 and selected_point !=None and selected_point != closest_point:

        #check if connections exists already
        for connection, distance in connections:
            if (connection[0] == closest_point and connection[1] == selected_point) or (connection[1] == closest_point and connection[0] == selected_point):
                return
        distance = get_distance(closest_point, selected_point)
        connections.append(((selected_point, closest_point), round(distance)))
        draw_line(selected_point, closest_point)
        print('Connection added: (' + str(selected_point) + ',' + str(closest_point) + ')')
        draw_point(closest_point, True)
        draw_point(selected_point)
        selected_point = closest_point
    else:
        # dont add if points to close
        if distance < 10:
            return
        # add point
        print('Point added: (' + str(x) + ',' + str(y) + ')')
        points.append(click_point)
        draw_point(click_point)

    
def right_click(event):
    # select point
    global points
    global selected_point

    click_point = (event.x,event.y)
    
    # get closest point
    closest_point, distance = get_closest_point(click_point)

    # select
    if distance < 30:
        if selected_point != None:
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

    click_point = (event.x,event.y)

    # get closest point
    closest_point, distance = get_closest_point(click_point)

    # delete
    if distance < 15:
        # if deleted point is selected, unselect
        if selected_point == closest_point:
            selected_point =None

        # remove from points
        points.remove(closest_point)

        # remove from connections
        keep = []
        for (p1, p2), distance in connections:
            if p1 != closest_point and p2 != closest_point:
                keep.append(((p1,p2), distance))
        
        connections = keep
        #redraw
        redraw()

    else:
        print('No point near')

def key_press(event):
    global points
    global selected_point

    # move point small amounts
    if event.keysym == 'Up':
        if selected_point !=None:
            change_point(selected_point, (selected_point[0], selected_point[1] - 1))
            redraw()
    elif event.keysym == 'Down':
        if selected_point !=None:
            change_point(selected_point, (selected_point[0], selected_point[1] + 1))
            redraw()
    elif event.keysym == 'Left':
        if selected_point !=None:
            change_point(selected_point, (selected_point[0] - 1, selected_point[1]))
            redraw()
    elif event.keysym == 'Right':
        if selected_point !=None:
            change_point(selected_point, (selected_point[0] + 1, selected_point[1]))
            redraw()


    elif event.keysym == 'Escape':
        pass
    elif event.keysym == 'Space':
        pass
    elif event.keysym == 'Tab':
        pass
    print(event)

def redraw():
    global points
    global connections
    global selected_point
    global canvas
    global img

    canvas.delete("all")
    canvas.create_image(0,0, anchor=NW, image=img)
    canvas.pack(expand = YES, fill = BOTH)

    # draw all connections
    for connection, distance in connections:
        draw_line(connection[0], connection[1])

    # draw all points
    for point in points:
        if point == selected_point:
            draw_point(point, True)
        else:
            draw_point(point)

def change_point(old, new):
    
    global points
    global connections
    global selected_point

    # change points
    new_points = []
    for p in points:
        if old != p:
            new_points.append(p)
    new_points.append(new)

    points = new_points

    # change connections
    new_connections = []
    for c, distance in connections:
        if old == c[0]:
            new_connections.append(((new, c[1]), distance))
        elif  old == c[1]:
            new_connections.append(((new, c[0]), distance))
        else:
            new_connections.append((c, distance))
    connections = new_connections
    selected_point = new

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
selected_point =None

# set dir to parent dir of this dir
os.chdir(Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute())

master = Tk()
master.protocol("WM_DELETE_WINDOW", close_window)
master.title( "Draw route" )
canvas = Canvas(master, 
           width=canvas_width, 
           height=canvas_height)

img = PhotoImage(file="maps/goldene_hoehle/normal.png")
img = img.zoom(scale, scale)

canvas.create_image(0,0, anchor=NW, image=img)

canvas.pack(expand = YES, fill = BOTH)
canvas.focus_set()
canvas.bind( "<Button-3>", right_click )
canvas.bind( "<Button-2>", middle_click )
canvas.bind( "<Button-1>", left_click )
canvas.bind("<Key>", key_press)
#TODO: Add keylistener, 
# arrow keys to move points
# tab to select next

# # message = Label( master, text = "Press and Drag the mouse to draw" )
# message.pack( side = BOTTOM )

# load netfile
points, connections = load_path('maps/goldene_hoehle/paths/net.txt', scale)

# draw them
redraw()
    
mainloop()

