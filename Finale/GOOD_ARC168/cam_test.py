import cv2

video = cv2.VideoCapture(0)

while True:
    ret, ogframe = video.read()
    cv2.imshow('output', ogframe)
    print(video.get(cv2.CAP_PROP_CONTRAST))
    #print(ogframe.shape)
    if cv2.waitKey(1) == ord('q'):
        break
