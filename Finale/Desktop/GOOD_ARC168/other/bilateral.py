import cv2
import numpy as np

video = cv2.VideoCapture(0)

minCanny = 25
maxCanny = 35
sigmaColor, sigmaSpace, pixel_neighborhood_diameter = [80, 80, 1]
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

def sigmaColorChanged(x):
    global sigmaColor
    sigmaColor = x
def sigmaSpaceChanged(x):
    global sigmaSpace
    sigmaSpace = x
def pixel_neighborhood_diameterChanged(x):
    global pixel_neighborhood_diameter
    pixel_neighborhood_diameter = x

cv2.namedWindow("cannySliders")
cv2.createTrackbar('minCanny', 'cannySliders', 0, 255, minCannyChanged)
cv2.createTrackbar('maxCanny', 'cannySliders', 0, 255, maxCannyChanged)
cv2.setTrackbarPos('minCanny','cannySliders', minCanny)
cv2.setTrackbarPos('maxCanny','cannySliders', maxCanny)

cv2.createTrackbar('dilation','cannySliders', 0, 25, dilationChanged)
cv2.setTrackbarPos('dilation','cannySliders', dilation)


cv2.createTrackbar('sigmaColor', 'cannySliders', 0, 200, sigmaColorChanged)
cv2.createTrackbar('sigmaSpace', 'cannySliders', 0, 200, sigmaSpaceChanged)
cv2.createTrackbar('pixel_neighborhood_diameter', 'cannySliders', 0, 30, pixel_neighborhood_diameterChanged)
cv2.setTrackbarPos('sigmaColor','cannySliders', sigmaColor)
cv2.setTrackbarPos('sigmaSpace','cannySliders', sigmaSpace)
cv2.setTrackbarPos('pixel_neighborhood_diameter','cannySliders', pixel_neighborhood_diameter)

while True:
    ret, ogframe = video.read()
    
    bilateral_blur = cv2.bilateralFilter(ogframe, pixel_neighborhood_diameter, sigmaColor, sigmaSpace) # 15 # https://www.geeksforgeeks.org/python-bilateral-filtering/

    edges = cv2.Canny(bilateral_blur, minCanny, maxCanny)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(dilation, dilation)) #9, 9
    dilated = cv2.dilate(edges, kernel)

    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    empty = np.zeros((ogframe.shape[0], ogframe.shape[1]), np.uint8)

    for i in range(len(contours)-1, -1, -1):
        
        (x, y, w, h) = cv2.boundingRect(contours[i])
        center_x = int(x + w/2)
        center_y = abs(int(y - h/2))

        widthRatio = w/ogframe.shape[1]
        heightRatio = h/ogframe.shape[0]

        if widthRatio >= 0.1 and heightRatio >= 0.1:
            
            surface = cv2.contourArea(contours[i])
            surface_percentage = surface/(w*h)

            if surface_percentage > 0.1:
                print("Found this")
                print("center", center_x, center_y)
                print("size ratios", widthRatio, heightRatio)
                print("surface percentage", surface_percentage)
                cv2.drawContours(empty, [contours[i]], -1, (255, 255, 255), -1) #-1
                break


    cv2.imshow('edges', edges)
    cv2.imshow('dilated', dilated)
    #cv2.imshow('bilateral_blur', bilateral_blur)
    #cv2.imshow('empty', empty)
    #cv2.imshow('ogframe', ogframe)
    if cv2.waitKey(1) == ord('q'):
        break
