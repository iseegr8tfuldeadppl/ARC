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
    
    kernel = np.ones((9, 9), np.uint8) #(9, 9), (15, 15), (31, 31 does not improve much upon the (15, 15))
    morphed = cv2.morphologyEx(ogframe, cv2.MORPH_OPEN, kernel, iterations=1)

    edges = cv2.Canny(morphed, minCanny, maxCanny)

    kernel2 = np.ones((9, 9), np.uint8) #(9, 9), (15, 15), (31, 31 does not improve much upon the (15, 15))
    morphed2 = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(morphed2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #contours = sorted(contours, key=lambda x: cv2.contourArea(x))

    
    empty = np.zeros((ogframe.shape[0], ogframe.shape[1]), np.uint8)

    print("contours found", len(contours))
    contours_accepted = 0
    for i in range(len(contours)-1, -1, -1):
        
        (x, y, w, h) = cv2.boundingRect(contours[i])
        center_x = int(x + w/2) / ogframe.shape[1]
        center_y = abs(int(y - h/2)) / ogframe.shape[0]

        widthRatio = w/ogframe.shape[1]
        heightRatio = h/ogframe.shape[0]

        if widthRatio >= 0.1 and heightRatio >= 0.1:
            print("center", center_x, center_y)
            print(widthRatio, heightRatio)
            
            
            surface = cv2.contourArea(contours[i])
            surface_percentage = surface/(w*h)
            print("surface_percentage", surface_percentage)
                
            #cv2.drawContours(empty, [contours[i]], -1, (255, 255, 255), -1) #-1
            contours_accepted += 1
            break
    print("contours accepted", contours_accepted)
    
    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(31, 31))
    #dilated = cv2.dilate(empty, kernel)

    '''
    contours2, _ = cv2.findContours(empty, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours2 = sorted(contours2, key=lambda x: cv2.contourArea(x))
    for i in range(len(contours2)-1, -1, -1):
        
        (x, y, w, h) = cv2.boundingRect(contours2[i])
        center_x = int(x + w/2)
        center_y = abs(int(y - h/2))

        widthRatio = w/ogframe.shape[1]
        heightRatio = h/ogframe.shape[0]

        if widthRatio >= 0.1 and heightRatio >= 0.1:
            print("center", center_x, center_y)
            print(widthRatio, heightRatio)
            cv2.drawContours(ogframe, [contours2[i]], -1, (0, 255, 0), -1) #-1
    '''


    cv2.imshow('ogframe', ogframe)
    if cv2.waitKey(1) == ord('q'):
        break
