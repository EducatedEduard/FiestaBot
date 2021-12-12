import cv2

# Cascade Haar file
# http://note.sonots.com/SciSoftware/haartraining.html#e134e74e

# detect mutliscale https://www.geeksforgeeks.org/detect-an-object-with-opencv-python/

# img_ore = cv2.imread('C:/Users/Josel/OneDrive/Desktop/python/fiesta autominer/trainimages/ores/(17).png')
img_vid = cv2.imread('C:/Users/Josel/OneDrive/Desktop/python/fiesta autominer/trainimages/unedited/(1).png')
ores = []

print(cv2.__file__)

cv2.opencv_createsamples

#read all ores
i = 0

while True:
    i += 1
    path = 'C:/Users/Josel/OneDrive/Desktop/python/fiesta autominer/trainimages/ores/(' + str(i) + ').png'     
    ores.append(cv2.imread(path))

    if i == 100:
        break

i = 0

for ore in ores:

    #TODO check other methods
    result = cv2.matchTemplate(ore, img_vid, cv2.TM_SQDIFF_NORMED)

    found = img_vid.detectMultiScale(ore, 
                                   minSize =(20, 20))

    # We want the minimum squared difference
    mn,_,mnLoc,_ = cv2.minMaxLoc(result)

    # Draw the rectangle:
    # Extract the coordinates of our best match
    MPx,MPy = mnLoc

    # Step 2: Get the size of the template. This is the same size as the match.
    trows,tcols = ore.shape[:2]

    # Step 3: Draw the rectangle on large_image
    cv2.rectangle(img_vid, (MPx,MPy),(MPx+tcols,MPy+trows),(0,0,255),2)

# Display the original image with the rectangle around the match.
cv2.imshow('output',img_vid)

# The image is only displayed if we call this
cv2.waitKey(0)