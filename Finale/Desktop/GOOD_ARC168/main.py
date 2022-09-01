# to execute
# don't run it with sudo (messes with camera)
# python main.py
# check all # CAN GIVE ERRORS HERE: comments




from fcntl import F_SEAL_SEAL
from gbase import *
from nrfstuff import *
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
    "minSizeRatio": 0.2,
    "maxSizeRatio": 0.9,
    "rectangle_width_to_height_ratio": 0.3,
    "countours_to_display": 7,
    "minGrayThresh": 127, #195
    "maxGrayThresh": 255, #255
    "minCannyThresh": 20, # 13
    "maxCannyThresh": 39, # 13
    "gaussianBlurKernelSize": 5,
    "errorFromCenterX": 0.2,
    "errorFromCenterY": 0.15,

    "dilation": 6,
    "sigmaColor": 80,
    "sigmaSpace": 80,
    "pixel_neighborhood_diameter": 1
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
        "Max Vote Period": 7 # # CAN GIVE ERRORS HERE: comments: it used to be 2 seconds of voting
    }

def resolveVotes():
    #totalVotes = votes["Circles"] + votes["Squares"] + votes["Rectangles"] + votes["Triangles"]
    
    # IMPORTANT-TOOLS: for seeing what robot is voting for
    print("votes", votes["Circles"], votes["Squares"], votes["Rectangles"], votes["Triangles"])

    shape_with_most_votes = "Circles"
    shape_most_votes = votes["Circles"]
    if votes["Squares"] > shape_most_votes:
        shape_most_votes = votes["Squares"]
        shape_with_most_votes = "Squares"
    if votes["Rectangles"] > shape_most_votes:
        shape_most_votes = votes["Rectangles"]
        shape_with_most_votes = "Rectangles"
    if votes["Triangles"] > shape_most_votes:
        shape_most_votes = votes["Triangles"]
        shape_with_most_votes = "Triangles"

    minimum_vote_requirement = 3
    if shape_most_votes <= minimum_vote_requirement:
        print("sadly less than", minimum_vote_requirement, "minimum vote requirement with", shape_most_votes, "votes")
        shape_with_most_votes = "Unknown"
    else:
        print("shape_most_votes", shape_most_votes)



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

# Cargo: Arrays
cargoPositions = [{ # initial arm stance
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

# Arm: Arrays
squarePositions = [{ # initial arm stance
        "mouth": 5,
        "bottom": 92,
        "tilt": 92,
        "spine": 42
    },
    { # go down to face the shape before going forward
        "mouth": 5,
        "bottom": 92,
        "tilt": 0,
        "spine": 65
    },
    { # get to cupping the shape
        "mouth": 0,
        "bottom": 92,
        "tilt": 6,
        "spine": 92
    },
    { # close mouth
        "mouth": 60,
        "bottom": 92,
        "tilt": 6,
        "spine": 92
    },
    { # get back up
        "mouth": 60,
        "bottom": 92,
        "tilt": 100,
        "spine": 49
    },
    { # turn around
        "mouth": 60,
        "bottom": 0,
        "tilt": 100,
        "spine": 49
    },
    { # let go
        "mouth": 0,
        "bottom": 0,
        "tilt": 100,
        "spine": 49
    }]
armPositions = {
    "Squares": squarePositions.copy(),
    "Triangles": squarePositions.copy()
}
 
# GUI: Vars
fontScale = 0.8
thickness = 1
colorNameThickness = 2

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

# Cargo: Vars
viewed_cargoArmPosition = 0
cargoArmPosition = 0
cargoArmUpdated = False
go_cargo_arm = False
last_go_cargo_arm_execusion = 0

# Arm: Vars
last_go_arm_execusion = 0
delay_between_arm_execusions = 0.2 # 0.2 or 0.5 or 2 seconds
armPosition = 0
viewed_armPosition = 0
viewed_armShapePosition = 0 # just a random default
armShapes = ["Squares", "Circles", "Triangles", "Rectangles"]
shape = "Square" # shapes: Square, Rectangle, Circle, Triangle
armUpdated = False
go_arm = False

# Car Control: Vars
carControlOn = False
forth, left, right, back = [False, False, False, False]

# Line Follower: Vars
lineFollowerRunning = False

# HSV variables
ogframe = None
threshold = None
dst = None
edges = None
dilated = None
selectedColor = "Unselected"
selectedColorIndex = 0
buttons_height, buttons_width = [50, 250]
mask = None
button_down = False
color_button_down = False

# Canny variables
print("you  might need to tune epsilon")
epsilonCoeff = 0.01 # 0.04
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

mode = "Unselected" # modes: Vision, Line Follower, Arm, Car Control, Cargo Pass, NRF & Unselected
print("Initial mode is", mode, "btw")
receivedAnglesBoolean = False 
@app.route('/motion', methods=["GET", "POST"])
def motion_feed():
    global mode
    global current_manual_cargo_positions, receivedAnglesBoolean
    if request.method == 'GET':
        if current_manual_cargo_positions == None:
            current_manual_cargo_positions = {
                "mouth": armPositions["Squares"][0]["mouth"],
                "bottom": armPositions["Squares"][0]["bottom"],
                "tilt": armPositions["Squares"][0]["tilt"],
                "spine": armPositions["Squares"][0]["spine"],
            }

            print("was unable to return arm positions bcz it wasn't inited yet")
            return "OOF, arm positions not inited yet"
        else:
            return str(str(current_manual_cargo_positions["bottom"]) + "," + str(current_manual_cargo_positions["spine"]) + "," + str(current_manual_cargo_positions["tilt"]) + "," + str(current_manual_cargo_positions["mouth"]) + "," + "90")
    elif request.method == 'POST':
        receivedAngles = request.form.get("angles").split(",")
        donrf = request.form.get("turn_off_arm_request")
        receivedAnglesBoolean = True
        current_manual_cargo_positions = {
            "mouth": int(receivedAngles[3]),
            "bottom": int(receivedAngles[0]),
            "tilt": int(receivedAngles[2]),
            "spine": int(receivedAngles[1]),
        }
        print(donrf)  
        if donrf == "1":
            print("SWITCHING MODE TO NRF")
            mode = "NRF"
        elif donrf == "2":
            print("SWITCHING MODE TO Cargo")
            mode = "Cargo Pass"
        print("received", current_manual_cargo_positions)
        return "Switched to " + str(mode)

current_manual_cargo_positions = None
@app.route('/mode', methods=["GET", "POST"])
def mode_feed():
    global mode, detectedColor, detectedShape, allowToPickUp, pickupRequest
    global current_manual_cargo_positions # cargo pass
    global votes # vision
    if request.method == 'GET':
        return str(mode)
    elif request.method == 'POST':

        # for some preprocessing before going ahead with updating the mode
        tempMode = request.form.get("mode")

        if tempMode == "Cargo Pass":
            
            current_manual_cargo_positions = {
                "mouth": armPositions["Squares"][0]["mouth"],
                "bottom": armPositions["Squares"][0]["bottom"],
                "tilt": armPositions["Squares"][0]["tilt"],
                "spine": armPositions["Squares"][0]["spine"],
            }

        elif tempMode == "Vision":
            votes = resetVotes()

        #if autoStartMode:
        elif tempMode == "Arm":
            detectedShape = "Unknown"

        mode = tempMode
        print("Received a mode update:", tempMode)
        return mode
    return "Unknowncommandbozo"

@app.route('/car', methods=["GET", "POST"])
def car_feed():
    global mode, forth, left, right, back
    if request.method == 'GET':
        return str(mode)
    elif request.method == 'POST':
        states = request.form.get("states")
        forth, left, right, back = [state=="true" for state in states.split(" ")]
        return "Thanksbozo"
    return "Unknown command bozo"

@app.route('/allowpickup', methods=["GET", "POST"])
def pickup_feed():
    global allowToPickUp, pickupRequest
    if request.method == 'GET':
        return str(str(shapes) + ":" + str(pickupRequest) + ":" + str(detectedShape) + ":" + str(detectedColor) + ":" + str(mode))
    elif request.method == 'POST':
        allowToPickUp = True
        pickupRequest = False
        return "Thanksbozo"
    return "Unknowncommandbozo"

@app.route('/startAuto', methods=["GET", "POST"])
def startAuto_feed():
    global mode
    '''
    if request.method == 'GET':
        return str(mode)
    elif request.method == 'POST':
        if request.form.get("autoStarted") == "true":
            mode = "Vision"
        else:
            mode = "Unselected"
        return "Thanksbozo"
    '''
    return "Unknowncommandbozo"

@app.route('/', methods=["GET", "POST"])
def ping_feed():
    return "cool"

# Server: start server function
def server():
    app.run(host='0.0.0.0', port=1337, threaded=True)


# Saving functions
def saveVars():
    with open(filename, 'wb') as f:
        #"hsvs": hsvs, "cargoPositions": cargoPositions, "currentarm": {"CURRENT_MOUTH": CURRENT_MOUTH, "CURRENT_SPINE": CURRENT_SPINE, "CURRENT_TILT": CURRENT_TILT, "CURRENT_BOTTOM": CURRENT_BOTTOM}
        pickle.dump({"canny": canny, "armPositions": armPositions}, f) #, "current_manual_cargo_positions": current_manual_cargo_positions
        #print("Successfully saved")
def loadVars():
    global hsvs, canny, armPositions, cargoPositions, current_manual_cargo_positions
    global CURRENT_MOUTH, CURRENT_SPINE, CURRENT_TILT, CURRENT_BOTTOM
    with open(filename, 'rb') as f:
        All = pickle.load(f)
        #if All.get("current_manual_cargo_positions") != None:
        #    current_manual_cargo_positions = All["current_manual_cargo_positions"]
        print("FORDEBUGG: you're not pulling canny")
        if All.get("canny") is not None:
            canny = All["canny"]
        print("FORDEBUGG: you're not pulling positions")
        if All.get("armPositions") is not None:
            armPositions["Squares"] = All["armPositions"]["Squares"]
            armPositions["Triangles"] = All["armPositions"]["Squares"]
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
'''
def updateButtons():
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
'''

'''
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
'''

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
def edgeDilationChanged(x):
    global canny
    canny["dilation"] = x
    notifySave()
def edgesigmaColorChanged(x):
    global canny
    canny["sigmaColor"] = x
    notifySave()
def edgeSigmaSpaceChanged(x):
    global canny
    canny["sigmaSpace"] = x
    notifySave()
def edgeDChanged(x):
    global canny
    canny["pixel_neighborhood_diameter"] = x
    notifySave()

# Cargo: Functions
def cargoMouthChanged(x):
    global cargoPositions
    cargoPositions[viewed_cargoArmPosition]["mouth"] = x
    notifySave()
def cargoBottomChanged(x):
    global cargoPositions
    cargoPositions[viewed_cargoArmPosition]["bottom"] = x
    notifySave()
def cargoTiltChanged(x):
    global cargoPositions
    cargoPositions[viewed_cargoArmPosition]["tilt"] = x
    notifySave()
def cargoSpineChanged(x):
    global cargoPositions
    cargoPositions[viewed_cargoArmPosition]["spine"] = x
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


# Mode Selection: GUI Functions

# Arm: Gui Functions
modeClickedButtonDown = False
def switchModeClicked(event, x, y, flags, param):
    global modeClickedButtonDown # gui stuff
    global mode # mode switching
    global current_manual_cargo_positions # cargo pass
    global detectedShape # arm mode
    global votes # vision

    if event==cv2.EVENT_LBUTTONDOWN:
        if not modeClickedButtonDown:
            modeClickedButtonDown = True

            # bottom most buttons
            # left shape in list
            # we have a different arm course of positions for different shapes
            if x < buttons_width//2:
                votes = resetVotes()
                mode = "Vision"
            elif x < buttons_width:
                detectedShape = "Unknown"
                mode = "Arm"
            elif x < (buttons_width*3)//2:
                mode = "Line Follower"
            elif x < buttons_width*2:
                mode = "Car Control"
            elif x < (buttons_width*5)//2:
                current_manual_cargo_positions = {
                    "mouth": armPositions["Squares"][0]["mouth"],
                    "bottom": armPositions["Squares"][0]["bottom"],
                    "tilt": armPositions["Squares"][0]["tilt"],
                    "spine": armPositions["Squares"][0]["spine"],
                }
                mode = "Cargo Pass"
            elif x < buttons_width*3:
                mode = "NRF"
            elif x < (buttons_width*7)//2:
                mode = "Unselected"
            print("Received a mode update:", mode)

    elif event==cv2.EVENT_LBUTTONUP:
        modeClickedButtonDown = False


# Arm: Gui Functions
def switchViewedPosition(event, x, y, flags, param):
    global button_down, viewed_armPosition, armPosition, armUpdated, viewed_armShapePosition
    global go_arm
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
                        go_arm = True
                        print("Go arm")
                    else:
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
 
# Vision: Inits
def VisionInits():
    # Canny: Inits
    cv2.namedWindow("cannySliders") #, cv2.WINDOW_AUTOSIZE
    emptyCannyImage = np.zeros((1, 300, 3), np.uint8)
    cv2.imshow("cannySliders", emptyCannyImage)
    cv2.createTrackbar("minCanny", "cannySliders", 0, 255, minCannyChanged)
    cv2.createTrackbar("maxCanny", "cannySliders", 0, 255, maxCannyChanged)
    cv2.createTrackbar("minsize", "cannySliders", 0, 100, minSizeChanged)
    cv2.createTrackbar("maxsize", "cannySliders", 0, 100, maxSizeChanged)
    cv2.createTrackbar("Gaussianblur", "cannySliders", 0, 15, gaussianBlurKernelSizeChanged)
    cv2.createTrackbar("ErrorX", "cannySliders", 0, 100, errorFromCenterXChanged)
    cv2.createTrackbar("ErrorY", "cannySliders", 0, 100, errorFromCenterYChanged)
    cv2.createTrackbar("Dilation", "cannySliders", 0, 25, edgeDilationChanged)
    cv2.createTrackbar("SigmaColor", "cannySliders", 0, 200, edgesigmaColorChanged)
    cv2.createTrackbar("SigmaSpace", "cannySliders", 0, 200, edgeSigmaSpaceChanged)
    cv2.createTrackbar("d", "cannySliders", 0, 30, edgeDChanged)

# Arm: Inits
def ArmInits():
    # Arm: Inits
    cv2.namedWindow("armSliders")
    cv2.setMouseCallback("armSliders", switchViewedPosition)
    cv2.createTrackbar('Mouth', 'armSliders', 0, 100, mouthChanged)
    cv2.createTrackbar('Bottom', 'armSliders', 0, 100, bottomChanged)
    cv2.createTrackbar('Tilt', 'armSliders', 0, 100, tiltChanged)
    cv2.createTrackbar('Spine', 'armSliders', 0, 100, spineChanged)

# Mode Selection: Inits
def modeSelectionInits():
    cv2.namedWindow("modeSelection")
    cv2.setMouseCallback("modeSelection", switchModeClicked)
    modeSelectionSwitchers = np.zeros((buttons_height, (buttons_width*7)//2, 3), np.uint8)
    modeSelectionSwitchers[:, 0 : buttons_width//2] = (255, 255, 255) # (B, G, R)
    modeSelectionSwitchers[:, buttons_width//2 : buttons_width] = (0, 0, 0)
    
    modeSelectionSwitchers[:, buttons_width : (buttons_width*3)//2] = (255, 255, 255) # (B, G, R)
    modeSelectionSwitchers[:, (buttons_width*3)//2 : buttons_width*2] = (0, 0, 0)
    
    modeSelectionSwitchers[:, buttons_width*2 : (buttons_width*5)//2] = (255, 255, 255) # (B, G, R)
    modeSelectionSwitchers[:, (buttons_width*5)//2 : buttons_width*3] = (0, 0, 0)
    
    modeSelectionSwitchers[:, buttons_width*3 : (buttons_width*7)//2] = (255, 255, 255) # (B, G, R)
    #modeSelectionSwitchers[:, (buttons_width*7)//2 : buttons_width*4] = (0, 0, 0)

    modeSelectionSwitchers = cv2.putText(modeSelectionSwitchers, "Vision", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness, cv2.LINE_AA)
    modeSelectionSwitchers = cv2.putText(modeSelectionSwitchers, "Arm", (10+buttons_width//2, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness, cv2.LINE_AA)
    modeSelectionSwitchers = cv2.putText(modeSelectionSwitchers, "Line", (10+buttons_width, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness, cv2.LINE_AA)
    modeSelectionSwitchers = cv2.putText(modeSelectionSwitchers, "Car", (10+(buttons_width*3)//2, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness, cv2.LINE_AA)
    modeSelectionSwitchers = cv2.putText(modeSelectionSwitchers, "Cargo", (10+buttons_width*2, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness, cv2.LINE_AA)
    modeSelectionSwitchers = cv2.putText(modeSelectionSwitchers, "NRF", (10+(buttons_width*5)//2, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness, cv2.LINE_AA)
    modeSelectionSwitchers = cv2.putText(modeSelectionSwitchers, "Unselected", (10+buttons_width*3, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness, cv2.LINE_AA)
    cv2.imshow("modeSelection", modeSelectionSwitchers)

def updateCanny():
    try:
        cv2.setTrackbarPos('minCanny','cannySliders', canny["minCannyThresh"])
        cv2.setTrackbarPos('maxCanny','cannySliders', canny["maxCannyThresh"])
        cv2.setTrackbarPos('Gaussianblur','cannySliders', canny["gaussianBlurKernelSize"])
        cv2.setTrackbarPos('minsize','cannySliders', int(canny["minSizeRatio"]*100))
        cv2.setTrackbarPos('maxsize','cannySliders', int(canny["maxSizeRatio"]*100))
        cv2.setTrackbarPos('ErrorX','cannySliders', int(canny["errorFromCenterX"]*100))
        cv2.setTrackbarPos('ErrorY','cannySliders', int(canny["errorFromCenterY"]*100))
        
        cv2.setTrackbarPos('Dilation','cannySliders', canny["dilation"])
        cv2.setTrackbarPos('SigmaColor','cannySliders', canny["sigmaColor"])
        cv2.setTrackbarPos('SigmaSpace','cannySliders', canny["sigmaSpace"])
        cv2.setTrackbarPos('d','cannySliders', canny["pixel_neighborhood_diameter"])
    except Exception as e:
        print(e)
        print("lol")


# Vision: Functions
def showWindows():
    modeSelectionInits()
    VisionInits()
    updateCanny()
    ArmInits()
    updateArmSliders()
    updateArmButtons()

# Arm: Functions
print("Wrap 2 is stopping before position index 6")
def wrap2(index):
    if index >= len(armPositions[armShapes[viewed_armShapePosition]]): ######len(armPositions[armShapes[viewed_armShapePosition]])
        return 0
    elif index < 0:
        return len(armPositions[armShapes[viewed_armShapePosition]])-1 ######len(armPositions[armShapes[viewed_armShapePosition]])-1
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
    buttons = np.ones((buttons_height, buttons_width, 3), np.uint8)
    # this entire code here without spaces in between is to just color the buttons according to next and previous color for ease of use don't ask why
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
    
    '''    
    shapeSwitchers = np.zeros((buttons_height, buttons_width, 3), np.uint8)
    shapeSwitchers[:,0:buttons_width//2] = (255, 255, 255) # (B, G, R)
    shapeSwitchers[:,buttons_width//2:buttons_width] = (0, 0, 0)
    shapeSwitchers = cv2.putText(shapeSwitchers, armShapes[wrap3(viewed_armShapePosition-1)], (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), thickness, cv2.LINE_AA)
    shapeSwitchers = cv2.putText(shapeSwitchers, armShapes[wrap3(viewed_armShapePosition+1)], (170, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness, cv2.LINE_AA)
    shapeSwitchers = cv2.putText(shapeSwitchers, armShapes[viewed_armShapePosition], (60, 17), cv2.FONT_HERSHEY_SIMPLEX, fontScale, (255, 0, 0), colorNameThickness, cv2.LINE_AA)
    '''
    numpy_vertical = np.vstack((buttons, apply)) #, shapeSwitchers

    cv2.imshow("armSliders", numpy_vertical)

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
    global saved
    # this is for debug mode with the menus only
    #if not autoStartMode:
    if armUpdated:
        armUpdated = False
        changed = go_to_coordinates(mode, viewed_armPosition, MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["mouth"], MOUTH_MIN, MOUTH_MAX), \
                            MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["bottom"], BOTTOM_MIN, BOTTOM_MAX), \
                            MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["tilt"], TILT_MIN, TILT_MAX), \
                            MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["spine"], SPINE_MIN, SPINE_MAX),
                            shape=armShapes[viewed_armShapePosition])
        #if changed:
        #    saved = False

    
                             
    elif go_arm:
        # this part is for testing arm sequences only (loop mode is on)
        # first part of if statment is delay between position and another, second part is delay between a sequence and another
        if time.time() - last_go_arm_execusion >= delay_between_arm_execusions or (time.time() - last_go_arm_execusion >= 2 and armPosition==0):
            # Menu: just to update the menu we are seeing
            if viewed_armPosition != armPosition:
                viewed_armPosition = armPosition
                updateArmSliders()
                updateArmButtons()

            changed = go_to_coordinates(mode, viewed_armPosition, MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["mouth"], MOUTH_MIN, MOUTH_MAX), \
                                MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["bottom"], BOTTOM_MIN, BOTTOM_MAX), \
                                MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["tilt"], TILT_MIN, TILT_MAX), \
                                MSFromPercent(armPositions[armShapes[viewed_armShapePosition]][armPosition]["spine"], SPINE_MIN, SPINE_MAX),
                                shape=armShapes[viewed_armShapePosition])
            #if changed:
            #    saved = False

            # wait between arm positions
            last_go_arm_execusion = time.time()

            # move to next arm position
            armPosition += 1
            armPosition = wrap2(armPosition)

def robotArm(Max):
    global armPosition, last_go_arm_execusion
    global saved

    checkArmUpdatedManually()

    # this is for auto mode, execute the sequence once and then stop
    #else:
    if time.time() - last_go_arm_execusion >= delay_between_arm_execusions:
        changed = go_to_coordinates(mode, armPosition, MSFromPercent(armPositions[detectedShape][armPosition]["mouth"], MOUTH_MIN, MOUTH_MAX), \
                            MSFromPercent(armPositions[detectedShape][armPosition]["bottom"], BOTTOM_MIN, BOTTOM_MAX), \
                            MSFromPercent(armPositions[detectedShape][armPosition]["tilt"], TILT_MIN, TILT_MAX), \
                            MSFromPercent(armPositions[detectedShape][armPosition]["spine"], SPINE_MIN, SPINE_MAX),
                            shape=detectedShape)
        #if changed:
        #    saved = False
        armPosition += 1
        last_go_arm_execusion = time.time()
        return armPosition < Max
    return True

# edge detection
def edgeCannyStuff():
    global votes, ogframe, dilated, edges
    bilateral_blur = cv2.bilateralFilter(ogframe, canny["pixel_neighborhood_diameter"], canny["sigmaColor"], canny["sigmaSpace"]) # 15 # https://www.geeksforgeeks.org/python-bilateral-filtering/

    edges = cv2.Canny(bilateral_blur, canny["minCannyThresh"], canny["maxCannyThresh"])

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(canny["dilation"], canny["dilation"])) #9, 9
    dilated = cv2.dilate(edges, kernel)

    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    #empty = np.zeros((ogframe.shape[0], ogframe.shape[1]), np.uint8)

    for i in range(len(contours)-1, -1, -1):
        
        (x, y, w, h) = cv2.boundingRect(contours[i])
        center_x = int(x + w/2)
        center_y = int(y + h/2)

        widthRatio = w/ogframe.shape[1]
        heightRatio = h/ogframe.shape[0]

        # if it's large enough
        if widthRatio >= canny["minSizeRatio"] and heightRatio >= canny["minSizeRatio"] and \
            widthRatio <= canny["maxSizeRatio"] and heightRatio <= canny["maxSizeRatio"]:
            


            # if it's off of center constraints
            x_center_of_img, y_center_of_img = (ogframe.shape[1]/2, ogframe.shape[0]/2) # x, y
            if abs(x_center_of_img - center_x) / x_center_of_img > canny["errorFromCenterX"] or \
                abs(y_center_of_img - center_y) / y_center_of_img > canny["errorFromCenterY"]:
                continue

            surface = cv2.contourArea(contours[i])
            surface_percentage = surface/(w*h)

            # if its surface is too small
            if surface_percentage < 0.3:
                continue

            # debugging
            print("C", (round(abs(x_center_of_img - center_x) / x_center_of_img, 2), round(abs(y_center_of_img - center_y) / y_center_of_img, 2)), \
                    "R", (round(widthRatio, 2), round(heightRatio, 2)), \
                    "%", round(surface_percentage, 2))

            cv2.drawContours(ogframe, [contours[i]], -1, (255, 255, 255), -1) #-1
            cv2.circle(ogframe, (center_x, center_y), 1, (0, 255, 0), 3)
            # IMPORTANT-TOOL: maximum center constraints
            ogframe = cv2.rectangle(ogframe, (int(x_center_of_img-x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img-y_center_of_img*canny["errorFromCenterY"])), (int(x_center_of_img+x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img+y_center_of_img*canny["errorFromCenterY"])), (0, 255, 0), 1)

            # shape classification method
            if surface_percentage >= 0.56 and surface_percentage < 0.82: # and not len(approx)==4
                if mode != "Unselected":
                    votes["Circles"] += 1
                break

            if 0.35 < surface_percentage and surface_percentage < 0.55: 
                if mode != "Unselected":
                    votes["Triangles"] += 1
                break
            elif surface_percentage >= 0.82: #len(approx)==4 or 
                #print("width to height ratio", abs( 1 - float(w)/h ))
                canny["rectangle_width_to_height_ratio"] = 0.3 # CAN GIVE ERRORS HERE: i'm hardcoding this
                if  abs( 1 - float(w)/h ) < canny["rectangle_width_to_height_ratio"]: # DEBUGGING CODE: 0.1 here means if the width is maximally 10% longer or shorter than height then it's probably a square not a rectangle 
                    if mode != "Unselected":
                        votes["Squares"] += 1
                    break
                else:
                    if mode != "Unselected":
                        votes["Rectangles"] += 1
                    break
                break

 

def edge_detecting_shape():
    global cap, ogframe
    ret, ogframe = cap.read()
    #ogframetest = cv2.imread("imBGR.png")
    if ret:
        edgeCannyStuff()

motors_resetted = False
x_center_of_img, y_center_of_img = [None, None]
# Auto: Functions
def autoThread():
    global motors_resetted # Unselected mode
    global x_center_of_img, y_center_of_img
    global ogframe, cap, edges, dilated
    global allowToPickUp, pickupRequest, detectedColor, detectedShape, carControlOn, shapes, mode
    global armPosition, last_go_arm_execusion # arm mode
    global receivedAnglesBoolean # cargo pass
    global last_slider_update, saved
    global votes # decision system

    #mode = "Vision" # in auto mode, mode begins from vision
    print("AUTO: Vision mode") # always starts with vision
    firstVisionPermissionRequested = True
    while True:
        try:
            if cv2.waitKey(1) == ord('q'):
                break

            if firstVisionPermissionRequested: #ONLY ALLOW PICKUP AUTOMATICALLY AFTER THE VERY VERY FIRST LAUNCH ALLOWANCE
                allowToPickUp = True

            #if not comp_day:
            # save to pickle file
            if not saved:
                if time.time() - last_slider_update >= update_delay:
                    saved = True
                    print("saving", time.time())
                    last_slider_update = time.time()
                    saveVars()

            if mode == "Vision":
                resetLineFollower()
                carControlOn = False
                edge_detecting_shape()
                if time.time() - votes["Start Of Vote"] > votes["Max Vote Period"]:
                    detectedShape, detectedColor = resolveVotes()
                    print("detections", detectedShape, detectedColor)
                    votes = resetVotes()

                    if not firstVisionPermissionRequested:
                        if allowToPickUp:
                            firstVisionPermissionRequested = True
                        else:
                            if not pickupRequest:
                                print("Vision: (DEBUG: permission to start vision sent)")
                                pickupRequest = True

                    if detectedShape == "Unknown":
                        continue
 
                    if detectedShape == "Circles" or detectedShape == "Rectangles":
                        continue

                    print("you're not picking up")
                    #False and 
                    if firstVisionPermissionRequested:
                        pickupRequest = True
                        mode = "Arm"
                        print("AUTO: Arm mode (pickup request sent)")

                if not comp_day:
                    # DEBUGGING:
                    try:
                        # IMPORTANT-TOOLS: show these commented frames so u can tune the image
                        if x_center_of_img == None:
                            x_center_of_img, y_center_of_img = (int(ogframe.shape[1]/2), int(ogframe.shape[0]/2)) # x, y
                        #cv2.circle(dilated, (x_center_of_img, y_center_of_img), 1, 255, 3)
                        dilated = cv2.rectangle(dilated, (int(x_center_of_img-x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img-y_center_of_img*canny["errorFromCenterY"])), (int(x_center_of_img+x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img+y_center_of_img*canny["errorFromCenterY"])), 255, 1)
                        #cv2.imshow('edges', edges)
                        #dilated = cv2.rectangle(dilated, (int(x_center_of_img-x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img-y_center_of_img*canny["errorFromCenterY"])), (int(x_center_of_img+x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img+y_center_of_img*canny["errorFromCenterY"])), 255, 1)
                        cv2.imshow('dilated', dilated)
                        #cv2.imshow('output', ogframe)
                    except Exception as e:
                        print(e)

            elif mode == "Arm":
                resetLineFollower()
                checkArmUpdatedManually()
                carControlOn = False

                if allowToPickUp:
                    allowToPickUp = False

                    # pickup loop
                    armPosition = 0
                    if detectedShape != "Unknown":
                        while robotArm(len(armPositions[detectedShape])):
                            ret, ogframe = cap.read()
                            if cv2.waitKey(1) == ord('q'):
                                break
                            pass

                        # then re-execute the first position of the arm so it can return to point of start
                        armPosition = 0
                        last_go_arm_execusion = 0
                        while robotArm(1):
                            ret, ogframe = cap.read()
                            if cv2.waitKey(1) == ord('q'):
                                break
                            pass
                        armPosition = 0 # then reset arm position
                        turnOffArm() # DEBUG: then turn arm off
                        print("Finished pickup")

                        mode = "Vision"
                        print("AUTO: Vision mode")
                        votes = resetVotes()
                        # after pickup, either send us back to vision or move on to next step
                        '''
                        if shapes <= 0:
                            print("Ran outta shapes")
                            mode = "Car Control"
                            print("AUTO: Car Control mode")
                        else:
                            mode = "Vision"
                            print("AUTO: Vision mode")
                        '''
                    else:
                        checkArmUpdatedManually()

                if not comp_day:
                    if cv2.waitKey(1) == ord('q'):
                        break

            elif mode == "Car Control":
                carControl()

            elif mode == "Line Follower":
                carControlOn = False
                lineFollower()

            elif mode == "Cargo Pass":
                resetLineFollower()
                carControlOn = False

                if receivedAnglesBoolean:
                    receivedAnglesBoolean = False
                    changed = go_to_coordinates(mode, 0, MSFromPercent(current_manual_cargo_positions["mouth"], MOUTH_MIN, MOUTH_MAX), \
                                        MSFromPercent(current_manual_cargo_positions["bottom"], BOTTOM_MIN, BOTTOM_MAX), \
                                        MSFromPercent(current_manual_cargo_positions["tilt"], TILT_MIN, TILT_MAX), \
                                        MSFromPercent(current_manual_cargo_positions["spine"], SPINE_MIN, SPINE_MAX))

            elif mode == "NRF":
                resetLineFollower()
                carControlOn = False
                sendNRFFinishMsg(pi)

            elif mode == "Unselected":
                resetLineFollower()
                carControlOn = False

                if not motors_resetted:
                    motors_resetted = True
                    go_to_coordinates("Cargo Pass", 0, MSFromPercent(armPositions["Squares"][0]["mouth"], MOUTH_MIN, MOUTH_MAX), \
                        MSFromPercent(armPositions["Squares"][0]["bottom"], BOTTOM_MIN, BOTTOM_MAX), \
                        MSFromPercent(armPositions["Squares"][0]["tilt"], TILT_MIN, TILT_MAX), \
                        MSFromPercent(armPositions["Squares"][0]["spine"], SPINE_MIN, SPINE_MAX), \
                        shape="Squares")
                    turnOffArm()

                # show me what vision is doing without a voting system
                try:
                    edge_detecting_shape()
                    # IMPORTANT-TOOLS: show these commented frames so u can tune the image
                    if x_center_of_img == None:
                        x_center_of_img, y_center_of_img = (int(ogframe.shape[1]/2), int(ogframe.shape[0]/2)) # x, y
                    #cv2.circle(dilated, (x_center_of_img, y_center_of_img), 1, 255, 3)
                    dilated = cv2.rectangle(dilated, (int(x_center_of_img-x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img-y_center_of_img*canny["errorFromCenterY"])), (int(x_center_of_img+x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img+y_center_of_img*canny["errorFromCenterY"])), 255, 1)
                    #cv2.imshow('edges', edges)
                    #dilated = cv2.rectangle(dilated, (int(x_center_of_img-x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img-y_center_of_img*canny["errorFromCenterY"])), (int(x_center_of_img+x_center_of_img*canny["errorFromCenterX"]), int(y_center_of_img+y_center_of_img*canny["errorFromCenterY"])), 255, 1)
                    cv2.imshow('dilated', dilated)
                    #cv2.imshow('output', ogframe)
                except Exception as e:
                    print(e)

            if mode != "Unselected":
                motors_resetted = False

        except Exception as e:
            print("bruh", e)

# Saving/Loading Work
try:
    loadVars()
    print("Loaded previously saved color ranges")
except Exception as e:
    print(e)
    saveVars()
    print("First time launch, using defaultcolor ranges")

showWindows()

# HSV: select the first color mate
for colorName, _ in hsvs.items():
    selectedColor = colorName
    break

# init arm
go_to_coordinates("Cargo Pass", 0, MSFromPercent(armPositions["Squares"][0]["mouth"], MOUTH_MIN, MOUTH_MAX), \
    MSFromPercent(armPositions["Squares"][0]["bottom"], BOTTOM_MIN, BOTTOM_MAX), \
    MSFromPercent(armPositions["Squares"][0]["tilt"], TILT_MIN, TILT_MAX), \
    MSFromPercent(armPositions["Squares"][0]["spine"], SPINE_MIN, SPINE_MAX),
    shape="Squares")
#print("default poses", MSFromPercent(armPositions["Squares"][0]["mouth"], MOUTH_MIN, MOUTH_MAX), MSFromPercent(armPositions["Squares"][0]["bottom"], BOTTOM_MIN, BOTTOM_MAX), MSFromPercent(armPositions["Squares"][0]["tilt"], TILT_MIN, TILT_MAX), MSFromPercent(armPositions["Squares"][0]["spine"], SPINE_MIN, SPINE_MAX))
#print("default poses in percent", armPositions["Squares"][0]["mouth"], armPositions["Squares"][0]["bottom"], armPositions["Squares"][0]["tilt"], armPositions["Squares"][0]["spine"])

# Server: start server
thread = Thread(target=server)
thread.start()

# Main: loop
if autoStartMode:
    autoThread()
#else:
#    debugThread()