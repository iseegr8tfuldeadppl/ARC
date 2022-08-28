import cv2
import numpy as np

video = cv2.VideoCapture(0)

while True:
    ret, ogframe = video.read()
    kernel = np.ones((9, 9), np.uint8)
    image = cv2.morphologyEx(ogframe, cv2.MORPH_OPEN, kernel, iterations=1)
    cv2.imshow('output', image)
    #print(video.get(cv2.CAP_PROP_CONTRAST))
    #print(ogframe.shape)
    if cv2.waitKey(1) == ord('q'):
        break
