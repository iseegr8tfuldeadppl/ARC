import cv2
import numpy as np

video = cv2.VideoCapture(0)

rho = 1  # distance resolution in pixels of the Hough grid
theta = np.pi / 180  # angular resolution in radians of the Hough grid
'''
threshold = 15  # minimum number of votes (intersections in Hough grid cell)
min_line_length = 50  # minimum number of pixels making up a line
max_line_gap = 20  # maximum gap in pixels between connectable line segments
'''

minCanny = 13
maxCanny = 17
rho, thresholdd, min_line_length, max_line_gap = [1, 15, 50, 20]
def minCannyChanged(x):
    global minCanny
    minCanny = x
def maxCannyChanged(x):
    global maxCanny
    maxCanny = x

def rhoChanged(x):
    global rho
    rho = x
def thresholddChanged(x):
    global thresholdd
    thresholdd = x
def min_line_lengthChanged(x):
    global min_line_length
    min_line_length = x
def max_line_gapChanged(x):
    global max_line_gap
    max_line_gap = x

cv2.namedWindow("cannySliders")
cv2.createTrackbar('minCanny', 'cannySliders', 0, 255, minCannyChanged)
cv2.createTrackbar('maxCanny', 'cannySliders', 0, 255, maxCannyChanged)
cv2.setTrackbarPos('minCanny','cannySliders', minCanny)
cv2.setTrackbarPos('maxCanny','cannySliders', maxCanny)


cv2.createTrackbar('rho', 'cannySliders', 0, 200, rhoChanged)
cv2.createTrackbar('thresholdd', 'cannySliders', 0, 200, thresholddChanged)
cv2.createTrackbar('min_line_length', 'cannySliders', 0, 200, min_line_lengthChanged)
cv2.createTrackbar('max_line_gap', 'cannySliders', 0, 200, max_line_gapChanged)
cv2.setTrackbarPos('rho','cannySliders', rho)
cv2.setTrackbarPos('thresholdd','cannySliders', thresholdd)
cv2.setTrackbarPos('min_line_length','cannySliders', min_line_length)
cv2.setTrackbarPos('max_line_gap','cannySliders', max_line_gap)

while True:
    ret, ogframe = video.read()
    gray = cv2.cvtColor(ogframe, cv2.COLOR_BGR2GRAY)
    dst = cv2.GaussianBlur(gray, (5, 5), 0)

        
    kernel = np.ones((15, 15), np.uint8) #(9, 9), (15, 15), (31, 31 does not improve much upon the (15, 15))
    morphed = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel, iterations=1)

    edges = cv2.Canny(morphed, minCanny, maxCanny)

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(edges, rho, theta, thresholdd, np.array([]),
                        min_line_length, max_line_gap)

    for line in lines:
        for x1,y1,x2,y2 in line:
            cv2.line(ogframe,(x1,y1),(x2,y2),(255,0,0),5)

    '''
    try:
        for i in range(len(contours)-1, -1, -1):
            
            (x, y, w, h) = cv2.boundingRect(contours[i])
            #center_x = int(x + w/2)
            #center_y = int(y - h/2)

            widthRatio = w/ogframe.shape[1]
            heightRatio = h/ogframe.shape[0]

            if widthRatio >= 0.4 and heightRatio >= 0.4:
                print(widthRatio, heightRatio)
                cv2.drawContours(ogframe, [contours[i]], -1, (0, 255, 0), 2) #-1
    except Exception as e:
        print(e)
    '''


    #numpy_horizontal = np.hstack((ogframe, image))
    cv2.imshow('ogframe', ogframe)
    cv2.imshow('edges', edges)
    #print(video.get(cv2.CAP_PROP_CONTRAST))
    #print(ogframe.shape)
    if cv2.waitKey(1) == ord('q'):
        break
