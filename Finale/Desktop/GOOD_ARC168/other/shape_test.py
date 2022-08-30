import cv2
import numpy as np

video = cv2.VideoCapture(0)

cannyMin = 34
cannyMax = 40
epsilonCoeff = 0.04
HMin, SMin, VMin, HMax, SMax, VMax = [72, 92, 21, 141, 255, 255]
def cannyMinChanged(x):
    global cannyMin
    cannyMin = x
def cannyMaxChanged(x):
    global cannyMax
    cannyMax = x

def HMinChanged(x):
    global HMin
    HMin = x
def SMinChanged(x):
    global SMin
    SMin = x
def VMinChanged(x):
    global VMin
    VMin = x
def HMaxChanged(x):
    global HMax
    HMax = x
def SMaxChanged(x):
    global SMax
    SMax = x
def VMaxChanged(x):
    global VMax
    VMax = x

cv2.namedWindow("sliders")
cv2.createTrackbar('cannyMin', 'sliders', 0, 255, cannyMinChanged)
cv2.createTrackbar('cannyMax', 'sliders', 0, 255, cannyMaxChanged)


cv2.createTrackbar('HMin', 'sliders', 0, 179, HMinChanged)
cv2.createTrackbar('SMin', 'sliders', 0, 255, SMinChanged)
cv2.createTrackbar('VMin', 'sliders', 0, 255, VMinChanged)
cv2.createTrackbar('HMax', 'sliders', 0, 179, HMaxChanged)
cv2.createTrackbar('SMax', 'sliders', 0, 255, SMaxChanged)
cv2.createTrackbar('VMax', 'sliders', 0, 255, VMaxChanged)

cv2.setTrackbarPos('cannyMin','sliders', cannyMin)
cv2.setTrackbarPos('cannyMax','sliders', cannyMax)

cv2.setTrackbarPos('HMin','sliders', HMin)
cv2.setTrackbarPos('SMin','sliders', SMin)
cv2.setTrackbarPos('VMin','sliders', VMin)
cv2.setTrackbarPos('HMax','sliders', HMax)
cv2.setTrackbarPos('SMax','sliders', SMax)
cv2.setTrackbarPos('VMax','sliders', VMax)

while True:
    ret, ogframe = video.read()

    maskHSV = cv2.cvtColor(ogframe, cv2.COLOR_BGR2HSV)
    gray = cv2.inRange(maskHSV, (HMin, SMin, VMin), (HMax, SMax, VMax))

    gray = cv2.GaussianBlur(gray, (15, 15), cv2.BORDER_DEFAULT)
    #gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    
    edges = cv2.Canny(gray, cannyMin, cannyMax)
    _, threshold = cv2.threshold(edges, 127, 255, cv2.THRESH_BINARY)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
    dilated = cv2.dilate(threshold, kernel)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    emptyCannyImage = np.zeros(ogframe.shape, np.uint8)
    
    for contour in contours:
        approx = cv2.approxPolyDP(contour, epsilonCoeff * cv2.arcLength(contour, True), True)
        # method 2: finding center point of shape
        (x, y, w, h) = cv2.boundingRect(approx)
        center_x = int(x + w/2)
        center_y = int(y - h/2)

        widthRatio = w/ogframe.shape[1]
        heightRatio = h/ogframe.shape[0]

        if widthRatio > 0.1:
            print(len(approx))
            #cv2.fillPoly(emptyCannyImage, pts=[contour], color=(255,255,255))
            cv2.drawContours(emptyCannyImage, contour, -1, (255,255,255), -1)
    
    edgesBGR = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    cv2.imshow('output', emptyCannyImage)
    if cv2.waitKey(1) == ord('q'):
        break
