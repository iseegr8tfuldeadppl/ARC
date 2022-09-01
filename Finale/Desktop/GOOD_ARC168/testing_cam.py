
import cv2
video = cv2.VideoCapture(0)


while True:
    ret, ogframe = video.read()
    cv2.imshow('ogframe', ogframe)
    if cv2.waitKey(1) == ord('q'):
        break