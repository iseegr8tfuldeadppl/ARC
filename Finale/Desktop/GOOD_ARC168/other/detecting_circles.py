import cv2
import numpy as np

video = cv2.VideoCapture(0)
#prev_circle = None
#dist = lambda x1,y1,x2,y2: (x1-x2)**2+(y1-y2)**2

#minCanny = 6
#maxCanny = 13

while True:
    ret, ogframe = video.read()
    gray = cv2.cvtColor(ogframe, cv2.COLOR_BGR2GRAY)
    dst = cv2.GaussianBlur(gray, (17, 17), 0)
    circles = cv2.HoughCircles(dst, cv2.HOUGH_GRADIENT, 
                        1.,
                        100,  # min distance between two circles not to be merged
                        param1=10, # sensitivity
                        param2=30, # accuracy
                        minRadius=110,
                        maxRadius=1000) #https://www.youtube.com/watch?v=RaCwLrKuS1w&t=22s&ab_channel=CodeSavant

    if circles is not None:
        circles = np.uint16(np.around(circles))
        '''
        chosen = None
        for i in circles[0, :]:
            if chosen is None:
                chosen = i
            if prev_circle is not None:
                if dist(chosen[0], chosen[1], prev_circle[0], prev_circle[1]) <= dist(i[0], i[1], prev_circle[0], prev_circle[1]):
                    chosen = i
        cv2.circle(ogframe, (chosen[0], chosen[1]), 1, (0, 100, 100), 3)
        cv2.circle(ogframe, (chosen[0], chosen[1]), chosen[2], (255, 0, 255), 3)
        prevCircle = chosen
        '''
        for i in circles[0, :]:
            cv2.circle(ogframe, (i[0], i[1]), i[2], (255, 0, 255), 3)
            print("radius", i[2])


    cv2.imshow('ogframe', ogframe)
    if cv2.waitKey(1) == ord('q'):
        break
