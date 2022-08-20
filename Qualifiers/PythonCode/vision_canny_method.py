from tkinter import E
import cv2
from skimage import io
import keyboard
import numpy as np
from serial_communicator import send_command
from threading import Thread
import imutils


cap = cv2.VideoCapture('http://192.168.1.4:8080/video')

# important parameters
epsilonCoeff = 0.04
scale_percent = 100 # percent of original size
minSizeRatio, maxSizeRatio = (0.08, 0.35)
rectangle_width_to_height_ratio = 0.05
countours_to_display = 7

minGrayThresh, maxGrayThresh = (195, 255)
minCannyThresh, maxCannyThresh = (239, 40)

gaussianBlurKernelSize = 5

# TODO - Beginning of comp:
# 1. adjust scale_percent which downscales the size of the footage from the camera
# 2. adjust minSizeRatio and maxSizeRatio which is the minimum/max width or height in percents compared to the whole frame of the picture
# 3. if u need Pentagons and Hexagons, then uncomment their if statements
# 4. adjust epsilonCoeff, it was 0.01 maybe keep it as 0.04 rn idk test
# 5. adjust rectangle_width_to_height_ratio
# 6. adjust port, it's COM5 rn
# 7. adjust minCannyThresh, maxCannyThresh
# 8. adjust gaussianBlurKernelSize it's what blurs the image for canny to look even better
# 9. adjust countours_to_display


def hmChanged(x):
    global hm
    hm = x
def smChanged(x):
    global sm
    sm = x
def vmChanged(x):
    global vm
    vm = x

def hMChanged(x):
    global hM
    hM = x
def sMChanged(x):
    global sM
    sM = x
def vMChanged(x):
    global vM
    vM = x

def minSizeChanged(x):
    global minSizeRatio
    minSizeRatio = x/100
def maxSizeChanged(x):
    global maxSizeRatio
    maxSizeRatio = x/100

def minCannyChanged(x):
    global minCannyThresh
    minCannyThresh = x
def maxCannyChanged(x):
    global maxCannyThresh
    # just gotta keep the gaussian kernel size odd, which is odd lol
    maxCannyThresh = x

def gaussianBlurKernelSizeChanged(x):
    global gaussianBlurKernelSize
    gaussianBlurKernelSize = x

def vision_thread(arg):
    #for i in range(arg):
    #    pass
    global gaussianBlurKernelSize, minCannyThresh, maxCannyThresh, scale_percent, minSizeRatio, maxSizeRatio, rectangle_width_to_height_ratio, hm, sm, vm, hM, sM, vM

    # random vars ignore
    firstFrame = True
    dim = None

    cv2.namedWindow("output", cv2.WINDOW_AUTOSIZE)

    cv2.createTrackbar('min Canny', 'output', 0, 255, minCannyChanged)
    cv2.createTrackbar('max Canny', 'output', 0, 255, maxCannyChanged)

    cv2.createTrackbar('min size', 'output', 0, 100, minSizeChanged)
    cv2.createTrackbar('max size', 'output', 0, 100, maxSizeChanged)
    
    cv2.createTrackbar('Gaussian blur', 'output', 0, 15, gaussianBlurKernelSizeChanged)

    cv2.setTrackbarPos('min Canny','output', minCannyThresh)
    cv2.setTrackbarPos('max Canny','output', maxCannyThresh)
    
    cv2.setTrackbarPos('Gaussian blur','output', gaussianBlurKernelSize)

    cv2.setTrackbarPos('min size','output', int(minSizeRatio*100))
    cv2.setTrackbarPos('max size','output', int(maxSizeRatio*100))


    while True:
        ret, frame = cap.read()

        if ret:
            
            # DEBUGGING CODE: resizing large image coming from ur phone lol remove later
            #print('Original Dimensions : ',frame.shape)
            if firstFrame: # load image dimension once brk
                firstFrame = False
                width = int(frame.shape[1] * scale_percent / 100)
                height = int(frame.shape[0] * scale_percent / 100)
                dim = (width, height)
                
            # resize image
            frame = cv2.resize(frame, dim, interpolation = cv2.INTER_AREA)
            
            # method 3: canny edges with grayscale ranging process of detecting shapes:
            if gaussianBlurKernelSize % 2 == 0:
                dst = cv2.GaussianBlur(frame, (gaussianBlurKernelSize+1, gaussianBlurKernelSize+1), cv2.BORDER_DEFAULT)
            else:
                dst = cv2.GaussianBlur(frame, (gaussianBlurKernelSize, gaussianBlurKernelSize), cv2.BORDER_DEFAULT)
            
            gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)

            edges = cv2.Canny(gray, minCannyThresh, maxCannyThresh)
            _, threshold = cv2.threshold(edges, minGrayThresh, maxGrayThresh, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            #contours = contours[0] if imutils.is_cv2() else contours[1]
            contours = sorted(contours, key=lambda x: cv2.contourArea(x))

            # go thru every contour
            i = -1 # index brk
            #print("Contours:", len(contours))
            countours_weve_displayed = 0
            for contour in contours:
                i += 1 # index brk
            
                # here we are ignoring first counter because 
                # findcontour function detects whole image as shape
                if i == 0:
                    i = 1
                    continue

                if countours_weve_displayed > countours_to_display:
                    break
            

                # cv2.approxPloyDP() function to approximate the shape
                approx = cv2.approxPolyDP(contour, epsilonCoeff * cv2.arcLength(contour, True), True)


                # method 1: finding center point of shape
                #M = cv2.moments(contour)
                #if M['m00'] != 0.0:
                #    x = int(M['m10']/M['m00'])
                #    y = int(M['m01']/M['m00'])
                    
                # method 2: finding center point of shape
                (x, y, w, h) = cv2.boundingRect(approx)
                center_x = int(x + w/2)
                center_y = int(y - h/2)

                widthRatio = w/dim[0]
                heightRatio = h/dim[1]
    

                #print(widthRatio < minSizeRatio, heightRatio < maxSizeRatio, widthRatio > maxSizeRatio, heightRatio > maxSizeRatio)
                if (widthRatio < minSizeRatio or heightRatio < minSizeRatio) or (widthRatio > maxSizeRatio or heightRatio > maxSizeRatio): # DEBUGGING CODE: this is saying if the detected shape is larger than 30% of the entire frame in width then it's probably legit
                    continue
                print(countours_weve_displayed)
                countours_weve_displayed += 1


                #print("W ratio:", widthRatio, "H ratio:", heightRatio)

                # using drawContours() function
                cv2.drawContours(dst, [contour], 0, (0, 0, 255), 5)

                # putting shape name at center of each shape
                if len(approx) == 3:
                    cv2.putText(dst, 'Triangle', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
                elif len(approx) == 4:
                    
                    (_, _, w, h) = cv2.boundingRect(approx)
                    if  abs( 1 - float(w)/h ) < rectangle_width_to_height_ratio: # DEBUGGING CODE: 0.1 here means if the width is maximally 10% longer or shorter than height then it's probably a square not a rectangle 
                        cv2.putText(dst, 'Square', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                    else:
                        cv2.putText(dst, 'Rectangle', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
                #elif len(approx) == 5:
                #    cv2.putText(frame, 'Pentagon', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
                #elif len(approx) == 6:
                #    cv2.putText(frame, 'Hexagon', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
                else:
                    cv2.putText(dst, 'circle', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # show final resulting frame
            gray_3_channel = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            numpy_horizontal = np.hstack((dst, gray_3_channel))
            cv2.imshow('output', numpy_horizontal)
            
        else:
            print("Failed to load a frame")

        cv2.waitKey(1)
        if keyboard.is_pressed('q') == True or keyboard.is_pressed('esc') == True or 0xFF == ord('q'):
            break

        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break

thread = Thread(target = vision_thread, args = (10, ))

def main():
    serial = None
    pinged_first_time = False

    s_pressed = False
    m_pressed = False


    while True:
        if not pinged_first_time:
            pinged_first_time = True
            serial = send_command(serial, "INIT")

        if keyboard.is_pressed('m') == True:
            if not m_pressed:
                serial = send_command(serial, "MOVE")
            m_pressed = True
        else:
            m_pressed = False

        if keyboard.is_pressed('s') == True:
            if not s_pressed:
                serial = send_command(serial, "STOP")
            s_pressed = True
        else:
            s_pressed = False


        cv2.waitKey(1)
        if keyboard.is_pressed('q') == True or keyboard.is_pressed('esc') == True or 0xFF == ord('q'):
            if thread.is_alive():
                thread.join()
            break


if __name__ == "__main__":
    thread.start()
    main()
    
    #cv2.waitKey(0)
    cv2.destroyAllWindows()