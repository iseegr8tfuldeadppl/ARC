import cv2
import numpy as np

video = cv2.VideoCapture(0)

minCanny = 39
maxCanny = 50
one, two, three, four = [20, 7, 21, 0]
def minCannyChanged(x):
    global minCanny
    minCanny = x
def maxCannyChanged(x):
    global maxCanny
    maxCanny = x

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


cv2.createTrackbar('one', 'cannySliders', 0, 100, oneChanged)
cv2.createTrackbar('two', 'cannySliders', 0, 100, twoChanged)
cv2.createTrackbar('three', 'cannySliders', 0, 100, threeChanged)
cv2.createTrackbar('four', 'cannySliders', 0, 100, fourChanged)
cv2.setTrackbarPos('one','cannySliders', one)
cv2.setTrackbarPos('two','cannySliders', two)
cv2.setTrackbarPos('three','cannySliders', three)
cv2.setTrackbarPos('four','cannySliders', four)

while True:
    ret, ogframe = video.read()
    #gray = cv2.cvtColor(ogframe, cv2.COLOR_BGR2GRAY)
    #dst = cv2.GaussianBlur(gray, (17, 17), 0)
    #kernel = np.ones((31, 31), np.uint8) #(9, 9), (15, 15), (31, 31 does not improve much upon the (15, 15))
    #morphed = cv2.morphologyEx(ogframe, cv2.MORPH_OPEN, kernel, iterations=1)
    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
    #image = cv2.dilate(morphed, kernel)

        
    #gray = cv2.cvtColor(ogframe, cv2.COLOR_BGR2HSV)[:, :, 2]
    #gray_blurred = cv2.medianBlur(gray, 11)
    #kernel = np.ones((9, 9), np.uint8) #(9, 9), (15, 15), (31, 31 does not improve much upon the (15, 15))
    #morphed = cv2.morphologyEx(gray_blurred, cv2.MORPH_OPEN, kernel, iterations=1)
    
    kernel = np.ones((9, 9), np.uint8) #(9, 9), (15, 15), (31, 31 does not improve much upon the (15, 15))
    morphed = cv2.morphologyEx(ogframe, cv2.MORPH_OPEN, kernel, iterations=1)

    edges = cv2.Canny(morphed, minCanny, maxCanny)

    kernel2 = np.ones((9, 9), np.uint8) #(9, 9), (15, 15), (31, 31 does not improve much upon the (15, 15))
    morphed2 = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)


    
    cv2.imshow('morphed2', morphed2)
    cv2.imshow('edges', edges)
    if cv2.waitKey(1) == ord('q'):
        break
