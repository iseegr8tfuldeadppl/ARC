import cv2
import numpy as np

video = cv2.VideoCapture(0)

minCanny = 6
maxCanny = 13
def minCannyChanged(x):
    global minCanny
    minCanny = x
def maxCannyChanged(x):
    global maxCanny
    maxCanny = x

cv2.namedWindow("cannySliders")
cv2.createTrackbar('minCanny', 'cannySliders', 0, 255, minCannyChanged)
cv2.createTrackbar('maxCanny', 'cannySliders', 0, 255, maxCannyChanged)
cv2.setTrackbarPos('minCanny','cannySliders', minCanny)
cv2.setTrackbarPos('maxCanny','cannySliders', maxCanny)

while True:
    ret, ogframe = video.read()
    gray = cv2.cvtColor(ogframe, cv2.COLOR_BGR2GRAY)
    dst = cv2.GaussianBlur(gray, (17, 17), 0)
    kernel = np.ones((31, 31), np.uint8) #(9, 9), (15, 15), (31, 31 does not improve much upon the (15, 15))
    morphed = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel, iterations=1)
    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    #image = cv2.dilate(morphed, kernel)
    edges = cv2.Canny(morphed, minCanny, maxCanny)
    _, threshold = cv2.threshold(edges, 100, 255, cv2.THRESH_BINARY)
    

    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3, 3))
    #dilated = cv2.dilate(threshold, kernel)

    contours, hierarchy = cv2.findContours(threshold,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
    contours = sorted(contours, key=lambda x: cv2.contourArea(x))
    #print("contours", cv2.contourArea(contours[len(contours)-1]))
    #print("contours", cv2.contourArea(contours[len(contours)-2]))
    #print("contours", cv2.contourArea(contours[len(contours)-3]))
    #cv2.drawContours(ogframe, [contours[len(contours)-1]], -1, (0, 255, 0), 2) #-1
    #cv2.drawContours(ogframe, [contours[len(contours)-2]], -1, (0, 255, 0), 2) #-1
    #cv2.drawContours(ogframe, [contours[len(contours)-3]], -1, (0, 255, 0), 2) #-1
    try:
        if len(contours)>0:
            cv2.drawContours(ogframe, contours, 2, (0, 255, 0), 2) #-1
    except:
        pass
        


    #numpy_horizontal = np.hstack((ogframe, image))
    cv2.imshow('gray', gray)
    cv2.imshow('threshold', threshold)
    #print(video.get(cv2.CAP_PROP_CONTRAST))
    #print(ogframe.shape)
    if cv2.waitKey(1) == ord('q'):
        break
