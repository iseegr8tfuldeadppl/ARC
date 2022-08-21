# to execute
# don't run it with sudo (messes with camera)
# python main.py
# check all # CAN GIVE ERRORS HERE: comments



from fcntl import F_SEAL_SEAL
from gbase import *
from base import *
import cv2
import numpy as np
import pickle
import time
from flask import Flask, request
from threading import Thread
 

# Vision: Arrays
hsvs = { # https://stackoverflow.com/questions/10948589/choosing-the-correct-upper-and-lower-hsv-boundaries-for-color-detection-withcv
    "Green": {
        "range": {
            "min": [45, 51, 20],
            "max": [94, 255, 255]
        },
        "representation": (4, 234, 62) # BGR
    },
    "Yellow": {
        "range": {
            "min": [0, 0, 0],
            "max": [0, 0, 0]
        },
        "representation": (19, 253, 241) # BGR
    },
    "Blue": {
        "range": {
            "min": [0, 0, 0],
            "max": [0, 0, 0]
        },
        "representation": (253, 31, 19) # BGR
    },
    "Red1": {
        "range": {
            "min": [0, 0, 0],
            "max": [0, 0, 0]
        },
        "representation": (23, 17, 255) # BGR
    },
    "Red2": {
        "range": {
            "min": [0, 0, 0],
            "max": [0, 0, 0]
        },
        "representation": (23, 17, 255) # BGR
    },
    "Orange": {
        "range": {
            "min": [0, 0, 0],
            "max": [0, 0, 0]
        },
        "representation": (19, 171, 253) # BGR
    }
}
canny = {
    "minSizeRatio": 0.06,
    "maxSizeRatio": 0.75,
    "rectangle_width_to_height_ratio": 0.4,
    "countours_to_display": 7,
    "minGrayThresh": 127, #195
    "maxGrayThresh": 255, #255
    "minCannyThresh": 34,
    "maxCannyThresh": 40,
    "gaussianBlurKernelSize": 5,
    "errorFromCenterX": 0.3,
    "errorFromCenterY": 0.3
}


# Canny & HSV: Functions
types_of_shapes = 4
types_of_colors = 5
print("Setup for", types_of_shapes, "types of shapes")
def resetVotes():
    return {
        "Circles": 0,
        "Squares": 0,
        "Rectangles": 0,
        "Triangles": 0,
        "Red": 0,
        "Blue": 0,
        "Green": 0,
        "Yellow": 0,
        "Orange": 0,
        "Start Of Vote": time.time(),
        "Max Vote Period": 2 # 1 second of voting
    }

def resolveVotes():
    totalVotes = votes["Circles"] + votes["Squares"] + votes["Rectangles"] + votes["Triangles"]
    shape_with_most_votes = "Circles"
    shape_most_votes = votes["Circles"]
    #if votes["Circles"] == 1: # if vote of circles was only one then bruh don't take it into account
    #    shape_most_votes = 0
    if votes["Squares"] > shape_most_votes:
        shape_most_votes = votes["Squares"]
        shape_with_most_votes = "Squares"
    if votes["Rectangles"] > shape_most_votes:
        shape_most_votes = votes["Rectangles"]
        shape_with_most_votes = "Rectangles"
    if votes["Triangles"] > shape_most_votes:
        shape_most_votes = votes["Triangles"]
        shape_with_most_votes = "Triangles"

    if shape_most_votes == 0:
        shape_with_most_votes = "Unknown"

    '''
    if shape_with_most_votes == "Circles" and totalVotes < 3: # if it was deemed a circle, lemme confirm t9i9a
        # simply if it even is able to find 4 vertices, it's most likely a square, circles can't do that
        if votes["Rectangles"] > 0:
            shape_most_votes = votes["Rectangles"]
            shape_with_most_votes = "Rectangles"
        elif votes["Squares"] > 0:
            shape_most_votes = votes["Squares"]
            shape_with_most_votes = "Squares"

    # simply if it even is able to find 3 vertices, it's most likely a triangle, circles can't do that
    if votes["Triangles"] > 0:
        shape_most_votes = votes["Triangles"]
        shape_with_most_votes = "Triangles"
    '''



    color_with_most_votes = "Unknown"
    color_most_votes = 0
    index = 0
    for name, value in votes.items():

        if index >= types_of_colors + types_of_shapes:
            break
        elif index == types_of_shapes:
            color_most_votes = value
            color_with_most_votes = name
        elif index > types_of_shapes:
            if value >= color_most_votes:
                color_most_votes = value
                color_with_most_votes = name
        index += 1

    if color_most_votes == 0:
        color_with_most_votes = "Unknown"

    return shape_with_most_votes, color_with_most_votes

# Canny & HSV: Vars
votes = resetVotes()

# Arm: Functions
def percentFromMS(position, Min, Max):
    if position < Min:
        return 0
    elif position > Max:
        return 100
    else:
        return int((position-Min)*100/(Max-Min))
def MSFromPercent(percent, Min, Max):
    if percent <= 0:
        return Min
    elif percent >= 100:
        return Max
    else:
        return int((Max-Min)*(percent/100) + Min)
# Arm: Arrays

armPositions = {
    "Squares": [{ # initial arm stance
        "mouth": 33,
        "bottom": 50,
        "tilt": 37,
        "spine": 33
    },
    { # go right above the shape or so
        "mouth": 25,
        "bottom": 45,
        "tilt": 0,
        "spine": 88
    },
    { # get to cupping the shape
        "mouth": 53,
        "bottom": 45,
        "tilt": 0,
        "spine": 88
    },
    { # close mouth
        "mouth": 52,
        "bottom": 45,
        "tilt": 38,
        "spine": 37
    },
    { # initial arm stance again
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    },
    { # turn around to cargo
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    },
    { # let go into cargo
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    }],


    "Circles": [{ # initial arm stance
        "mouth": 33,
        "bottom": 50,
        "tilt": 37,
        "spine": 33
    },
    { # go right above the shape or so
        "mouth": 25,
        "bottom": 45,
        "tilt": 0,
        "spine": 88
    },
    { # get to cupping the shape
        "mouth": 53,
        "bottom": 45,
        "tilt": 0,
        "spine": 88
    },
    { # close mouth
        "mouth": 52,
        "bottom": 45,
        "tilt": 38,
        "spine": 37
    },
    { # initial arm stance again
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    },
    { # turn around to cargo
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    },
    { # let go into cargo
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    }],


    "Triangles": [{ # initial arm stance
        "mouth": 33,
        "bottom": 50,
        "tilt": 37,
        "spine": 33
    },
    { # go right above the shape or so
        "mouth": 25,
        "bottom": 45,
        "tilt": 0,
        "spine": 88
    },
    { # get to cupping the shape
        "mouth": 53,
        "bottom": 45,
        "tilt": 0,
        "spine": 88
    },
    { # close mouth
        "mouth": 52,
        "bottom": 45,
        "tilt": 38,
        "spine": 37
    },
    { # initial arm stance again
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    },
    { # turn around to cargo
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    },
    { # let go into cargo
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    }],


    "Rectangles": [{ # initial arm stance
        "mouth": 33,
        "bottom": 50,
        "tilt": 37,
        "spine": 33
    },
    { # go right above the shape or so
        "mouth": 25,
        "bottom": 45,
        "tilt": 0,
        "spine": 88
    },
    { # get to cupping the shape
        "mouth": 53,
        "bottom": 45,
        "tilt": 0,
        "spine": 88
    },
    { # close mouth
        "mouth": 52,
        "bottom": 45,
        "tilt": 38,
        "spine": 37
    },
    { # initial arm stance again
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    },
    { # turn around to cargo
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    },
    { # let go into cargo
        "mouth": percentFromMS(MOUTH_REST, MOUTH_MIN, MOUTH_MAX),
        "bottom": percentFromMS(BOTTOM_REST, BOTTOM_MIN, BOTTOM_MAX),
        "tilt": percentFromMS(TILT_REST, TILT_MIN, TILT_MAX),
        "spine": percentFromMS(SPINE_REST, SPINE_MIN, SPINE_MAX)
    }]
}

# Auto Thread: Vars
ogShapes = 1
shapes = ogShapes
allowToPickUp = False
detectedColor = "Unknown"
detectedShape = "Unknown"
autoStartMode = True
pickupRequest = False
comp_day = False
print("comp_day is", comp_day)

# Vision: Vars
cap = cv2.VideoCapture(0)
#print(cap.get(cv2.CAP_PROP_CONTRAST))
#print(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#print(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#cap.set(3, 640)  # Set horizontal resolution cv2.CAP_PROP_FRAME_WIDTH
#cap.set(4, 480)  # Set vertical resolution cv2.CAP_PROP_FRAME_HEIGHT
#cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)    # Needed to set exposure manually
#cap.set(cv2.CAP_PROP_EXPOSURE, 900)          # 900ms exposure as per SOST
#cap.set(cv2.CAP_PROP_FPS, (1/0.9))            # Sets FPS accordingly


# Arm: Vars
last_go_arm_execusion = 0
delay_between_arm_execusions = 0.2 # 0.2 or 0.5 or 2 seconds
arm_windows_shown = False
armPosition = 0
viewed_armPosition = 0
viewed_armShapePosition = 0 # just a random default
armShapes = ["Squares", "Circles", "Triangles", "Rectangles"]
shape = "Square" # shapes: Square, Rectangle, Circle, Triangle
armUpdated = False
go_arm = False
go_arm_index = 0

# Car Control: Vars
carControlOn = False
forth, left, right, back = [False, False, False, False]

# Line Follower: Vars
lineFollowerRunning = False

# HSV variables
ogframe = None
threshold = None
dst = None
windows_shown = False
selectedColor = "Unselected"
selectedColorIndex = 0
buttons_height, buttons_width = [50, 250]
mask = None
button_down = False
color_button_down = False

# Canny variables
epsilonCoeff = 0.04
scale_percent = 100 # percent of original size

# Saving variables
last_slider_update = time.time()
saved = False
update_delay = 0.5 # save updates if it's been 2 seconds since sliders were updated
filename = "variables.pickle"


# Server: Functions
app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return "Bozo"

mode = "Unselected" # modes: Vision, Line Follower, Arm, Car Control, Cargo Pass & Unselected
print("Initial mode is", mode, "btw")
@app.route('/mode', methods=["GET", "POST"])
def mode_feed():
    global mode, shapes, detectedColor, detectedShape, allowToPickUp, pickupRequest
    if request.method == 'GET':
        return mode
    elif request.method == 'POST':

        # for some preprocessing before going ahead with updating the mode
        tempMode = request.form.get("mode")

        #if autoStartMode:
        if tempMode == "Arm":
            #allowToPickUp = False
            pickupRequest = True
            if shapes < 0:
                shapes = ogShapes
        if tempMode == "Vision": # so if we send it back to shapes just detect one more shape before wanting to move
            if shapes < 0:
                shapes = ogShapes
                detectedColor = "Unknown"
                detectedShape = "Unknown"

        mode = request.form.get("mode")
        print("Received a mode update:", mode)
        return "Thanks, bozo"
    return "Unknown command bozo"

@app.route('/car', methods=["GET", "POST"])
def car_feed():
    global mode, forth, left, right, back
    if request.method == 'GET':
        return mode
    elif request.method == 'POST':
        states = request.form.get("states")
        forth, left, right, back = [state=="true" for state in states.split(" ")]
        return "Thanks, bozo"
    return "Unknown command bozo"

@app.route('/allowpickup', methods=["GET", "POST"])
def pickup_feed():
    global allowToPickUp, pickupRequest
    if request.method == 'GET':
        return str(shapes) + ":" + str(pickupRequest) + ":" + str(detectedShape) + ":" + str(detectedColor) + ":" + str(mode)
    elif request.method == 'POST':
        allowToPickUp = True
        pickupRequest = False
        print("hey")
        return "Thanks, bozo"
    return "Unknown command bozo"

@app.route('/startAuto', methods=["GET", "POST"])
def startAuto_feed():
    global mode
    if request.method == 'GET':
        return str(mode)
    elif request.method == 'POST':
        if request.form.get("autoStarted") == "true":
            mode = "Vision"
        else:
            mode = "Unselected"
        return "Thanks, bozo"
    return "Unknown command bozo"

# Server: start server function
def server():
    app.run(host='0.0.0.0', port=1337, threaded=True)


# Saving functions
def saveVars():
    with open(filename, 'wb') as f:
        pickle.dump({"hsvs": hsvs, "canny": canny, "armPositions": armPositions}, f)
        #print("Successfully saved")
def loadVars():
    global hsvs, canny, armPositions
    with open(filename, 'rb') as f:
        All = pickle.load(f)
        if All.get("hsvs") != None:
            hsvs = All["hsvs"]
        #print("FORDEBUGG: you're not pulling canny")
        if All.get("canny") != None:
            canny = All["canny"]
        #print("FORDEBUGG: you're not pulling positions")
        if All.get("armPositions") != None:
            armPositions = All["armPositions"]
def notifySave():
    global saved, last_slider_update
    saved = False
    last_slider_update = time.time()

# HSV Functions
def HMinChanged(x):
    global hsvs
    hsvs[selectedColor]["range"]["min"][0] = x
    notifySave()
def SMinChanged(x):
    global hsvs
    hsvs[selectedColor]["range"]["min"][1] = x
    notifySave()
def VMinChanged(x):
    global hsvs
    hsvs[selectedColor]["range"]["min"][2] = x
    notifySave()
def HMaxChanged(x):
    global hsvs
    hsvs[selectedColor]["range"]["max"][0] = x
    notifySave()
def SMaxChanged(x):
    global hsvs
    hsvs[selectedColor]["range"]["max"][1] = x
    notifySave()
def VMaxChanged(x):
    global hsvs
    hsvs[selectedColor]["range"]["max"][2] = x
    notifySave()
def wrap(index):
    if index >= len(hsvs):
        return 0
    elif index < 0:
        return len(hsvs)-1
    else:
        return index
def updateButtons():
    fontScale = 0.8
    thickness = 1
    colorNameThickness = 2

    buttons = np.ones((buttons_height, buttons_width, 3), np.uint8)
    # this entire coode here without spaces in between is to just color the buttons according to next and previous color for ease of use don't ask why
    previous_index = selectedColorIndex - 1
    next_index = selectedColorIndex + 1
    previous_index = wrap(previous_index)
    next_index = wrap(next_index)
    index = 0
    previous_color = None
    next_color = None
    for colorName, colorContent in hsvs.items():
        if index == previous_index:
            previous_color = colorContent["representation"]
        elif index == next_index:
            next_color = colorContent["representation"]
        index += 1

    buttons[:,0:buttons_width//2] = previous_color      # (B, G, R)
    buttons[:,buttons_width//2:buttons_width] = next_color
    buttons = cv2.putText(buttons, selectedColor, (85, 17), cv2.FONT_HERSHEY_SIMPLEX, fontScale, hsvs[selectedColor]["representation"], colorNameThickness, cv2.LINE_AA)
    
    buttons = cv2.putText(buttons, "Previous", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0,0,0), thickness, cv2.LINE_AA)
    buttons = cv2.putText(buttons, "Next", (160, 35), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0,0,0), thickness, cv2.LINE_AA)
    cv2.imshow("sliders", buttons)
def updateSliders():
    global selectedColor
    #print("selectedColor", selectedColor)
    index = 0
    for colorName, colorContent in hsvs.items():
        if index == selectedColorIndex:
            #print("colorName", colorName)
            selectedColor = colorName
            cv2.setTrackbarPos('HMin', 'sliders', colorContent["range"]["min"][0])  
            cv2.setTrackbarPos('SMin', 'sliders', colorContent["range"]["min"][1])  
            cv2.setTrackbarPos('VMin', 'sliders', colorContent["range"]["min"][2])  
            cv2.setTrackbarPos('HMax', 'sliders', colorContent["range"]["max"][0])  
            cv2.setTrackbarPos('SMax', 'sliders', colorContent["range"]["max"][1])  
            cv2.setTrackbarPos('VMax', 'sliders', colorContent["range"]["max"][2])  
            break
        index += 1

def switchColor(event, x, y, flags, param):
    global color_button_down, selectedColorIndex
    if event==cv2.EVENT_LBUTTONDOWN:
        if not color_button_down:
            color_button_down = True

            # previous
            if x < buttons_width // 2:
                selectedColorIndex -= 1
                selectedColorIndex = wrap(selectedColorIndex)
    
            # next
            else:
                selectedColorIndex += 1
                selectedColorIndex = wrap(selectedColorIndex)

            updateSliders()
            updateButtons()

    elif event==cv2.EVENT_LBUTTONUP:
        color_button_down = False

# Canny Functions
def minSizeChanged(x):
    global Canny
    canny["minSizeRatio"] = x/100
    notifySave()
def maxSizeChanged(x):
    global Canny
    canny["maxSizeRatio"] = x/100
    notifySave()
def errorFromCenterXChanged(x):
    global Canny
    canny["errorFromCenterX"] = x/100
    notifySave()
def errorFromCenterYChanged(x):
    global Canny
    canny["errorFromCenterY"] = x/100
    notifySave()
def minCannyChanged(x):
    global canny
    canny["minCannyThresh"] = x
    notifySave()
def maxCannyChanged(x):
    global canny
    # just gotta keep the gaussian kernel size odd, which is odd lol
    canny["maxCannyThresh"] = x
    notifySave()
def gaussianBlurKernelSizeChanged(x):
    global canny
    canny["gaussianBlurKernelSize"] = x
    notifySave()

# Arm: Functions
def mouthChanged(x):
    global armPositions
    
    armPositions[armShapes[viewed_armShapePosition]][viewed_armPosition]["mouth"] = x
    notifySave()
def bottomChanged(x):
    global armPositions
    armPositions[armShapes[viewed_armShapePosition]][viewed_armPosition]["bottom"] = x
    notifySave()
def tiltChanged(x):
    global armPositions
    armPositions[armShapes[viewed_armShapePosition]][viewed_armPosition]["tilt"] = x
    notifySave()
def spineChanged(x):
    global armPositions
    armPositions[armShapes[viewed_armShapePosition]][viewed_armPosition]["spine"] = x
    notifySave()
def updateArmSliders():
    cv2.setTrackbarPos('Mouth', 'armSliders', armPositions[armShapes[viewed_armShapePosition]][viewed_armPosition]["mouth"])
    cv2.setTrackbarPos('Bottom', 'armSliders', armPositions[armShapes[viewed_armShapePosition]][viewed_armPosition]["bottom"])
    cv2.setTrackbarPos('Tilt', 'armSliders', armPositions[armShapes[viewed_armShapePosition]][viewed_armPosition]["tilt"])
    cv2.setTrackbarPos('Spine', 'armSliders', armPositions[armShapes[viewed_armShapePosition]][viewed_armPosition]["spine"])

def switchViewedPosition(event, x, y, flags, param):
    global button_down, viewed_armPosition, armPosition, armUpdated, viewed_armShapePosition
    global go_arm, go_arm_index
    if event==cv2.EVENT_LBUTTONDOWN:
        if not button_down:
            button_down = True

            # bottom most buttons
            # left shape in list
            # we have a different arm course of positions for different shapes
            if y > buttons_height * 2:
                if x < buttons_width // 2:
                    viewed_armShapePosition -= 1
                    viewed_armShapePosition = wrap3(viewed_armShapePosition)
                    viewed_armPosition = 0 # always resets to zero
                else:
                    viewed_armShapePosition += 1
                    viewed_armShapePosition = wrap3(viewed_armShapePosition)
                    viewed_armPosition = 0 # always resets to zero

            # bottom buttons
            # apply to arm
            elif y > buttons_height:
                if x < buttons_width // 2:
                    armPosition = viewed_armPosition
                    armUpdated = True
                    #print("Applied position at index", armPosition, "to arm")
                else:
                    if not go_arm:
                        go_arm_index = 0
                        go_arm = True
                        print("Go arm")
                    else:
                        go_arm_index = 0
                        go_arm = False
                        print("Stop arm")

            # top buttons
            else:
                # previous
                if x < buttons_width // 2:
                    viewed_armPosition -= 1
                    viewed_armPosition = wrap2(viewed_armPosition)
        
                # next
                else:
                    viewed_armPosition += 1
                    viewed_armPosition = wrap2(viewed_armPosition)

            updateArmSliders()
            updateArmButtons()

    elif event==cv2.EVENT_LBUTTONUP:
        button_down = False

# Canny Work
contours = []
def cannyStuff():
    global contours
    global ogframe
    global threshold, dst # debugging
    global votes # for decisions
    #dst = cv2.GaussianBlur(mask, (9, 9), cv2.BORDER_DEFAULT)
    #edges = cv2.Canny(mask, canny["minCannyThresh"], canny["maxCannyThresh"])
    #_, threshold = cv2.threshold(edges, canny["minGrayThresh"], canny["maxGrayThresh"], cv2.THRESH_BINARY)
    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3, 3))
    #dilated = cv2.dilate(edges, kernel)

    #contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    #contours = contours[0] if imutils.is_cv2() else contours[1]
    #contours = sorted(contours, key=lambda x: cv2.contourArea(x))

    # go thru every contour
    for i in range(len(contours)-1, -1, -1):
        contour = contours[i]
    
        # here we are ignoring first counter because 
        # findcontour function detects whole image as shape
        #if i == 0:
        #    i = 1
        #    continue

        # cv2.approxPloyDP() function to approximate the shape
        approx = cv2.approxPolyDP(contour, epsilonCoeff * cv2.arcLength(contour, True), True)
            
        # method 2: finding center point of shape
        (x, y, w, h) = cv2.boundingRect(contour)
        center_x = int(x + w/2)
        center_y = int(y - h/2)

        widthRatio = w/ogframe.shape[1]
        heightRatio = h/ogframe.shape[0]

        if abs(mask.shape[1]/2 - center_x) / mask.shape[1]/2 > canny["errorFromCenterX"]: #or abs(mask.shape[0]/2 - center_y) / mask.shape[0]/2 > canny["errorFromCenterY"]
            # CAN GIVE ERRORS HERE:print("Needs to be near the center")
            continue
        #print(widthRatio, heightRatio)
        if widthRatio < canny["minSizeRatio"] \
            or heightRatio < canny["minSizeRatio"] \
            or widthRatio > canny["maxSizeRatio"] \
            or heightRatio > canny["maxSizeRatio"]: # DEBUGGING CODE: this is saying if the detected shape is larger than 30% of the entire frame in width then it's probably legit
            # CAN GIVE ERRORS HERE:print("Outside size limitations")
            continue

        #print("Approx", len(approx))
        if len(approx) <= 1 or len(approx) > 30:
            continue

        surface = cv2.contourArea(contour)

        surface_percentage = surface/(w*h)
        cv2.drawContours(ogframe, [contour], 0, (255, 255, 255), 2)
            
        #print(surface*100/(w*h))
        if surface_percentage < 0.1:
            continue
        print("surface_percentage", surface_percentage)

        if surface_percentage >= 0.65 and surface_percentage < 0.87 and not len(approx)==4:
            votes["Circles"] += 1
            return

        if surface < w*h*0.65:
            votes["Triangles"] += 1
            return
        elif len(approx)==4 or surface_percentage >= 0.87:
            if  abs( 1 - float(w)/h ) < canny["rectangle_width_to_height_ratio"]: # DEBUGGING CODE: 0.1 here means if the width is maximally 10% longer or shorter than height then it's probably a square not a rectangle 
                votes["Squares"] += 1
                return
            else:
                votes["Rectangles"] += 1
                return

        
        #if len(approx) <= 3:
        #    #print("From x center", abs(mask.shape[1]/2 - center_x) / mask.shape[1]/2)
        #    votes["Triangles"] += 1
        #    return
        #elif len(approx) <= 5: # i've found rectangles to sometimes hit 6 as amaximum but circles seem to always be more idk
        #    # check if it's actually a triangle or not
        ##    if surface < w*h*0.65:
        #        #print("From x center", abs(mask.shape[1]/2 - center_x) / mask.shape[1]/2)
        #        votes["Triangles"] += 1
        #        return
        #    
        #    (_, _, w, h) = cv2.boundingRect(approx)
        #    if  abs( 1 - float(w)/h ) < canny["rectangle_width_to_height_ratio"]: # DEBUGGING CODE: 0.1 here means if the width is maximally 10% longer or shorter than height then it's probably a square not a rectangle 
        #        #print("From x center", abs(mask.shape[1]/2 - center_x) / mask.shape[1]/2)
        #        votes["Squares"] += 1
        #        return
        #    else:
        #        #print("From x center", abs(mask.shape[1]/2 - center_x) / mask.shape[1]/2)
        #        votes["Rectangles"] += 1
        #        return
        #elif len(approx) > 4:
        #    #print("From x center", abs(mask.shape[1]/2 - center_x) / mask.shape[1]/2)
        ##    votes["Circles"] += 1
        #    return
            


# HSV Work
def colorStuff():
    global contours
    global ogframe # debugging
    global mask
    global votes # decision system
    # detect contours of pieces
    for name, content in hsvs.items():

        if content["range"]["max"] == [0, 0, 0]:
            continue

        # since red is the online color with two ranges, i just hardcoded it, also 6days left before comp anw
        ogframeHSV = cv2.cvtColor(ogframe, cv2.COLOR_BGR2HSV)
        if name == "Red2":
            mask2 = cv2.inRange(ogframeHSV, tuple(content["range"]["min"]), tuple(content["range"]["max"]))
            mask = cv2.bitwise_or(mask, mask2)
        else:
            mask = cv2.inRange(ogframeHSV, tuple(content["range"]["min"]), tuple(content["range"]["max"]) )

        if name == "Red1":
            continue
        
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=lambda x: cv2.contourArea(x))
        
        if len(contours)>0:
            (x, y, w, h) = cv2.boundingRect(contours[len(contours)-1])
            x = int(x + w/2)
            y = int(y + h/2)
            center_x = int(x + w/2)
            center_y = int(y - h/2)

            colorContourWidthRatio = w/ogframe.shape[1]
            colorContourHeightRatio = h/ogframe.shape[0]    
            minColorContourWidthRatio = 0.2
            minColorContourHeightRatio = 0.2

            if colorContourWidthRatio < minColorContourWidthRatio \
                and colorContourHeightRatio  < minColorContourHeightRatio:
                # CAN GIVE ERRORS HERE:print("color blob needs to be big enuff")
                continue
            if abs(mask.shape[1]/2 - center_x) / mask.shape[1]/2 > canny["errorFromCenterX"]:
                # CAN GIVE ERRORS HERE:print("color blob needs to be near center")
                continue
            
            for contour in contours:
                (x, y, w, h) = cv2.boundingRect(contours[len(contours)-1])
                #cv2.drawContours(ogframe, [contour], 0, content["representation"], 2)
            if name == "Red2":
                votes["Red"] += 1
            else:
                votes[name] += 1
            return True
    return False
 
# Vision: Inits
emptyCannyImage = None
def VisionInits():
    global emptyCannyImage
    cv2.namedWindow("output")

    # HSV: Inits
    cv2.namedWindow("sliders")
    cv2.setMouseCallback("sliders", switchColor)
    cv2.createTrackbar('HMin', 'sliders', 0, 179, HMinChanged)
    cv2.createTrackbar('SMin', 'sliders', 0, 255, SMinChanged)
    cv2.createTrackbar('VMin', 'sliders', 0, 255, VMinChanged)
    cv2.createTrackbar('HMax', 'sliders', 0, 179, HMaxChanged)
    cv2.createTrackbar('SMax', 'sliders', 0, 255, SMaxChanged)
    cv2.createTrackbar('VMax', 'sliders', 0, 255, VMaxChanged)

    # Canny: Inits
    cv2.namedWindow("cannySliders") #, cv2.WINDOW_AUTOSIZE
    emptyCannyImage = np.zeros((1, 300, 3), np.uint8)
    cv2.imshow("cannySliders", emptyCannyImage)
    cv2.createTrackbar('min Canny', 'cannySliders', 0, 255, minCannyChanged)
    cv2.createTrackbar('max Canny', 'cannySliders', 0, 255, maxCannyChanged)
    cv2.createTrackbar('min size', 'cannySliders', 0, 100, minSizeChanged)
    cv2.createTrackbar('max size', 'cannySliders', 0, 100, maxSizeChanged)
    cv2.createTrackbar('Gaussian blur', 'cannySliders', 0, 15, gaussianBlurKernelSizeChanged)
    cv2.createTrackbar('Error X', 'cannySliders', 0, 100, errorFromCenterXChanged)
    cv2.createTrackbar('Error Y', 'cannySliders', 0, 100, errorFromCenterYChanged)

# Arm: Inits
def ArmInits():
    # Arm: Inits
    cv2.namedWindow("armSliders")
    cv2.setMouseCallback("armSliders", switchViewedPosition)
    cv2.createTrackbar('Mouth', 'armSliders', 0, 100, mouthChanged)
    cv2.createTrackbar('Bottom', 'armSliders', 0, 100, bottomChanged)
    cv2.createTrackbar('Tilt', 'armSliders', 0, 100, tiltChanged)
    cv2.createTrackbar('Spine', 'armSliders', 0, 100, spineChanged)

def updateCanny():
    cv2.setTrackbarPos('min Canny','cannySliders', canny["minCannyThresh"])
    cv2.setTrackbarPos('max Canny','cannySliders', canny["maxCannyThresh"])
    cv2.setTrackbarPos('Gaussian blur','cannySliders', canny["gaussianBlurKernelSize"])
    cv2.setTrackbarPos('min size','cannySliders', int(canny["minSizeRatio"]*100))
    cv2.setTrackbarPos('max size','cannySliders', int(canny["maxSizeRatio"]*100))
    cv2.setTrackbarPos('Error X','cannySliders', int(canny["errorFromCenterX"]*100))
    cv2.setTrackbarPos('Error Y','cannySliders', int(canny["errorFromCenterY"]*100))

# Vision: Functions
def hideWindows():
    global windows_shown
    if windows_shown:
        windows_shown = False
        cv2.destroyAllWindows()
def showWindows():
    global windows_shown
    if not windows_shown:
        windows_shown = True
        VisionInits()
        updateSliders()
        updateCanny()
        updateButtons()

# Arm: Functions
print("Wrap 2 is stopping before position index 6")
def wrap2(index):
    if index >= 6: ######len(armPositions[armShapes[viewed_armShapePosition]])
        return 0
    elif index < 0:
        return 5 ######len(armPositions[armShapes[viewed_armShapePosition]])-1
    else:
        return index
def wrap3(index): # for different shapes
    if index >= 4:
        return 0
    elif index < 0:
        return 3
    else:
        return index
def updateArmButtons():
    fontScale = 0.8
    thickness = 1
    colorNameThickness = 2

    buttons = np.ones((buttons_height, buttons_width, 3), np.uint8)
    # this entire coode here without spaces in between is to just color the buttons according to next and previous color for ease of use don't ask why
    previous_index = viewed_armPosition - 1
    next_index = viewed_armPosition + 1
    previous_index = wrap2(previous_index)
    next_index = wrap2(next_index)
    index = 0

    buttons[:,0:buttons_width//2] = (255, 255, 255)      # (B, G, R)
    buttons[:,buttons_width//2:buttons_width] = (0, 0, 0)
    
    buttons = cv2.putText(buttons, str(viewed_armPosition), (115, 17), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (255, 0, 0), colorNameThickness, cv2.LINE_AA)
    
    buttons = cv2.putText(buttons, "Previous", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (0,0,0), thickness, cv2.LINE_AA)
    buttons = cv2.putText(buttons, "Next", (160, 35), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (255, 255, 255), thickness, cv2.LINE_AA)
    buttons = cv2.putText(buttons, str(previous_index), (60, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), thickness, cv2.LINE_AA)
    buttons = cv2.putText(buttons, str(next_index), (180, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness, cv2.LINE_AA)
    
    
    apply = np.zeros((buttons_height, buttons_width, 3), np.uint8)
    apply[:,0:buttons_width//2] = (0, 0, 0)
    apply[:,buttons_width//2:buttons_width] = (255, 255, 255) # (B, G, R)
    apply = cv2.putText(apply, "Apply", (35, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness, cv2.LINE_AA)
    apply = cv2.putText(apply, "Go", (170, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness, cv2.LINE_AA)
    
    
    shapeSwitchers = np.zeros((buttons_height, buttons_width, 3), np.uint8)
    shapeSwitchers[:,0:buttons_width//2] = (255, 255, 255) # (B, G, R)
    shapeSwitchers[:,buttons_width//2:buttons_width] = (0, 0, 0)
    shapeSwitchers = cv2.putText(shapeSwitchers, armShapes[wrap3(viewed_armShapePosition-1)], (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness, cv2.LINE_AA)
    shapeSwitchers = cv2.putText(shapeSwitchers, armShapes[wrap3(viewed_armShapePosition+1)], (170, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness, cv2.LINE_AA)
    shapeSwitchers = cv2.putText(shapeSwitchers, armShapes[viewed_armShapePosition], (60, 17), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (255, 0, 0), colorNameThickness, cv2.LINE_AA)
    
    numpy_vertical = np.vstack((buttons, apply, shapeSwitchers))

    cv2.imshow("armSliders", numpy_vertical)
def hideArmWindows():
    global arm_windows_shown
    if arm_windows_shown:
        arm_windows_shown = False
        cv2.destroyAllWindows()
def showArmWindows():
    global arm_windows_shown
    if not arm_windows_shown:
        arm_windows_shown = True
        ArmInits()
        updateArmSliders()
        updateArmButtons()

# Line Follower: Functions
def resetLineFollower():
    global lineFollowerRunning
    if lineFollowerRunning:
        lineFollowerRunning = False
        reset()
    
def prepareLineFollower():
    global lineFollowerRunning
    if not lineFollowerRunning:
        lineFollowerRunning = True
        initLineFollower()
        start()

def lineFollower():
    global period_start
    prepareLineFollower()
    
    last_printed = None # debugging: printing values
    position = readSensors() # (use percentages) since pids have a sampling period, maybe read the sensors continously until period is over? and average all to have an accurate and reliable reading (use percentages)

    current_time = time.time()
    if current_time - period_start >= period:
        lSpd, rSpd = computePID(position)
        period_start = current_time
        
        PENA.ChangeDutyCycle(rSpd)
        PENB.ChangeDutyCycle(lSpd)

    # debugging: printing position value
    #if position != last_printed:
    #    print(position) 
    #    last_printed = position

# Car Control: Functions
def carControl():

    # things to execute the first time car control is ran
    global carControlOn
    if not carControlOn:
        carControlOn = True
        reset()

    if forth:
        Forth()
    if left:
        Left()
    if right:
        Right()
    if back:
        Back()

    if not forth and not left and not right and not back:
        reset()

# Arm: Functions
def checkArmUpdatedManually():
    global last_go_arm_execusion, armUpdated, armPosition, viewed_armPosition
    # this is for debug mode with the menus only
    #if not autoStartMode:
    if armUpdated:
        armUpdated = False
        go_to_coordinates(viewed_armPosition, MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["mouth"], MOUTH_MIN, MOUTH_MAX), \
                            MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["bottom"], BOTTOM_MIN, BOTTOM_MAX), \
                            MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["tilt"], TILT_MIN, TILT_MAX), \
                            MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["spine"], SPINE_MIN, SPINE_MAX))

    
                             
    elif go_arm:
        # this part is for testing arm sequences only (loop mode is on)
        # first part of if statment is delay between position and another, second part is delay between a sequence and another
        if time.time() - last_go_arm_execusion >= delay_between_arm_execusions or (time.time() - last_go_arm_execusion >= 2 and armPosition==0):
            # Menu: just to update the menu we are seeing
            if viewed_armPosition != armPosition:
                viewed_armPosition = armPosition
                updateArmSliders()
                updateArmButtons()

            go_to_coordinates(viewed_armPosition, MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["mouth"], MOUTH_MIN, MOUTH_MAX), \
                                MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["bottom"], BOTTOM_MIN, BOTTOM_MAX), \
                                MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["tilt"], TILT_MIN, TILT_MAX), \
                                MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["spine"], SPINE_MIN, SPINE_MAX))

            # wait between arm positions
            last_go_arm_execusion = time.time()

            # move to next arm position
            armPosition += 1
            armPosition = wrap2(armPosition)

def robotArm():
    global armPosition

    checkArmUpdatedManually()

    # this is for auto mode, execute the sequence once and then stop
    #else:
    if time.time() - last_go_arm_execusion >= delay_between_arm_execusions:
        go_to_coordinates(armPosition, MSFromPercent(armPositions[detectedShape][armPosition]["mouth"], MOUTH_MIN, MOUTH_MAX), \
                            MSFromPercent(armPositions[detectedShape][armPosition]["bottom"], BOTTOM_MIN, BOTTOM_MAX), \
                            MSFromPercent(armPositions[detectedShape][armPosition]["tilt"], TILT_MIN, TILT_MAX), \
                            MSFromPercent(armPositions[detectedShape][armPosition]["spine"], SPINE_MIN, SPINE_MAX))
        armPosition += 1
        return armPosition < len(armPositions[detectedShape])

    

# Vision: Functions
#count = 0 # DEBUGGING: counting fps
#start_of_second = time.time() # DEBUGGING: counting fps
def detecting_shape():
    #global count, start_of_second # DEBUGGING: counting fps
    global cap, ogframe
    ret, ogframe = cap.read()
    #ogframetest = cv2.imread("imBGR.png")
    if ret:
        ''' # fps counter 
        if time.time() - start_of_second > 1:
            count = 0
            start_of_second = time.time()
        count += 1
        print("Fps", count)
        '''
        detectedAColorMate = colorStuff()

        # if color stuff did detect a color with a considerable appearance of a blob then move onto doing canny
        if detectedAColorMate:
            cannyStuff()


# Auto: Functions
def autoThread():
    global allowToPickUp, pickupRequest, detectedColor, detectedShape, carControlOn, shapes, armPosition, mode
    global last_slider_update, saved
    global visionPermissionRequested
    global votes # decision system

    #mode = "Vision" # in auto mode, mode begins from vision
    print("AUTO: Vision mode") # always starts with vision
    visionPermissionRequested = False
    while True:
        if not comp_day:
            # save to pickle file
            if not saved:
                if time.time() - last_slider_update >= update_delay:
                    saved = True
                    last_slider_update = time.time()
                    saveVars()

        if mode == "Vision":
            if not comp_day:
                hideArmWindows()
                showWindows()

            resetLineFollower()
            carControlOn = False
            detecting_shape()
            if time.time() - votes["Start Of Vote"] > votes["Max Vote Period"]:
                detectedShape, detectedColor = resolveVotes()
                print("detections", detectedShape, detectedColor)
                votes = resetVotes()
                if not visionPermissionRequested:
                    print("Vision: (DEBUG: permission to move onto arm sent)")
                    visionPermissionRequested = True
                    allowToPickUp = False
                    pickupRequest = True

                if allowToPickUp: # i requested 
                    allowToPickUp = False
                    pickupRequest = True
                    shapes = ogShapes
                    mode = "Arm"
                    print("AUTO: Arm mode (pickup request sent)")

            if not comp_day:
                # DEBUGGING:
                try:
                    #edgesBGR = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
                    #thresholdBGR = cv2.cvtColor(threshold, cv2.COLOR_GRAY2BGR)
                    #dilatedBGR = cv2.cvtColor(dilated, cv2.COLOR_GRAY2BGR)
                    #contourMaskBGR = cv2.cvtColor(contourMask, cv2.COLOR_GRAY2BGR)
                    maskBGR = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
                    #dstBGR = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
                    numpy_horizontal = np.hstack((ogframe, maskBGR)) #thresholdBGR, contourCroppedOGFrame, contourCroppedFrame, edgesBGR, dst, ogframe
                    cv2.imshow('output', numpy_horizontal)
                except:
                    pass

                if cv2.waitKey(1) == ord('q'):
                    break

        elif mode == "Arm":
            if not comp_day:
                hideWindows()
                showArmWindows()
                
            resetLineFollower()
            checkArmUpdatedManually()
            carControlOn = False
            visionPermissionRequested = False

            if allowToPickUp and shapes > 0:
                allowToPickUp = False
                shapes -= 1

                detectedColor = "Unknown"
                detectedShape = "Unknown"

                # pickup loop
                armPosition = 0
                while robotArm():
                    pass

                # then re-execute the first position of the arm so it can return to point of start
                armPosition = 0
                robotArm()
                armPosition = 0 # then reset arm position
                turnOffArm() # DEBUG: then turn arm off

                # after pickup, either send us back to vision or move on to next step
                if shapes <= 0:
                    print("Ran outta shapes")
                    mode = "Car Control"
                    print("AUTO: Car Control mode")
                else:
                    mode = "Vision"
                    print("AUTO: Vision mode")

            if not comp_day:
                if cv2.waitKey(1) == ord('q'):
                    break

        elif mode == "Car Control":
            if not comp_day:
                hideWindows()
                hideArmWindows()
            carControl()
            visionPermissionRequested = False

        elif mode == "Line Follower":
            if not comp_day:
                hideWindows()
                hideArmWindows()
            carControlOn = False
            visionPermissionRequested = False
            lineFollower()

        elif mode == "Cargo Pass":
            if not comp_day:
                hideWindows()
                hideArmWindows()
            resetLineFollower()
            carControlOn = False
            visionPermissionRequested = False
        elif mode == "Unselected":
            shapes = ogShapes
            #if not comp_day:
            #    hideWindows()
            #    hideArmWindows()
            resetLineFollower()
            carControlOn = False
            visionPermissionRequested = False

def debugThread():
    global carControlOn
    while True:
        # save to pickle file
        if not saved:
            if time.time() - last_slider_update >= update_delay:
                saved = True
                last_slider_update = time.time()
                saveVars()

        if mode == "Vision":
            carControlOn = False
            hideArmWindows()
            showWindows()

            detecting_shape()

            # DEBUGGING:
            #cv2.imshow("sliders", buttons)
            #cv2.imshow("cannySliders", emptyCannyImage)
            #numpy_horizontal = np.hstack((ogframe, edges))
            cv2.imshow('output', ogframe)

            if cv2.waitKey(1) == ord('q'):
                break

        elif mode == "Arm":
            carControlOn = False
            hideWindows()
            showArmWindows()

            robotArm()

            if cv2.waitKey(1) == ord('q'):
                break

        elif mode == "Line Follower":
            carControlOn = False
            hideWindows()
            hideArmWindows()
            lineFollower()

        elif mode == "Car Control":
            hideWindows()
            hideArmWindows()
            carControl()

        elif mode == "Unselected":
            carControlOn = False
            hideWindows()
            hideArmWindows()

        elif mode == "Cargo Pass":
            carControlOn = False
            hideWindows()
            hideArmWindows()
            print("Cargo Pass")

# Saving/Loading Work
try:
    loadVars()
    print("Loaded previously saved color ranges")
except Exception as e:
    saveVars()
    print("First time launch, using defaultcolor ranges")

# HSV: select the first color mate
for colorName, _ in hsvs.items():
    selectedColor = colorName
    break



# Server: start server
thread = Thread(target=server)
thread.start()

# Main: loop
if autoStartMode:
    autoThread()
else:
    debugThread()