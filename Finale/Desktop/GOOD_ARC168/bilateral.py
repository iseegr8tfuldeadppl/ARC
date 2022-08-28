import cv2
import numpy as np

video = cv2.VideoCapture(0)

minCanny = 25
maxCanny = 35
one, two, three, four = [80, 80, 1, 0]
dilation = 5
def minCannyChanged(x):
    global minCanny
    minCanny = x
def maxCannyChanged(x):
    global maxCanny
    maxCanny = x
    
def dilationChanged(x):
    global dilation
    if x % 2 == 0:
        dilation = x+1
    else:
        dilation = x

def oneChanged(x):
    global one
    one = x
def twoChanged(x):
    global two
    two = x
def threeChanged(x):
    global three
    three = x
def fourChanged(x):
    global four
    four = x

cv2.namedWindow("cannySliders")
cv2.createTrackbar('minCanny', 'cannySliders', 0, 255, minCannyChanged)
cv2.createTrackbar('maxCanny', 'cannySliders', 0, 255, maxCannyChanged)
cv2.setTrackbarPos('minCanny','cannySliders', minCanny)
cv2.setTrackbarPos('maxCanny','cannySliders', maxCanny)

cv2.createTrackbar('dilation','cannySliders', 0, 25, dilationChanged)
cv2.setTrackbarPos('dilation','cannySliders', dilation)


cv2.createTrackbar('one', 'cannySliders', 0, 200, oneChanged)
cv2.createTrackbar('two', 'cannySliders', 0, 200, twoChanged)
cv2.createTrackbar('three', 'cannySliders', 0, 30, threeChanged)
cv2.createTrackbar('four', 'cannySliders', 0, 200, fourChanged)
cv2.setTrackbarPos('one','cannySliders', one)
cv2.setTrackbarPos('two','cannySliders', two)
cv2.setTrackbarPos('three','cannySliders', three)
cv2.setTrackbarPos('four','cannySliders', four)

while True:
    ret, ogframe = video.read()
    
    #kernel = np.ones((9, 9), np.uint8) #(9, 9), (15, 15), (31, 31 does not improve much upon the (15, 15))
    #morphed = cv2.morphologyEx(ogframe, cv2.MORPH_OPEN, kernel, iterations=1)

    bilateral_blur = cv2.bilateralFilter(ogframe,three,one,two) # 15 # https://www.geeksforgeeks.org/python-bilateral-filtering/

    edges = cv2.Canny(bilateral_blur, minCanny, maxCanny)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(dilation, dilation)) #9, 9
    dilated = cv2.dilate(edges, kernel)

    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #contours = sorted(contours, key=lambda x: cv2.contourArea(x))
    
    empty = np.zeros((ogframe.shape[0], ogframe.shape[1]), np.uint8)

    for i in range(len(contours)-1, -1, -1):
        
        (x, y, w, h) = cv2.boundingRect(contours[i])
        center_x = int(x + w/2) / ogframe.shape[1]
        center_y = abs(int(y - h/2)) / ogframe.shape[0]

        widthRatio = w/ogframe.shape[1]
        heightRatio = h/ogframe.shape[0]

        if widthRatio >= 0.1 and heightRatio >= 0.1:
            
            surface = cv2.contourArea(contours[i])
            surface_percentage = surface/(w*h)

            if surface_percentage > 0.1:
                print("center", center_x, center_y)
                print("size ratios", widthRatio, heightRatio)
                print("surface percentage", surface_percentage)
                cv2.drawContours(empty, [contours[i]], -1, (255, 255, 255), -1) #-1
                break


    cv2.imshow('edges', edges)
    cv2.imshow('dilated', dilated)
    cv2.imshow('bilateral_blur', bilateral_blur)
    cv2.imshow('empty', empty)
    if cv2.waitKey(1) == ord('q'):
        break
