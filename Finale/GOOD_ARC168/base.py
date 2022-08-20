import RPi.GPIO as GPIO
from time import sleep, time



# sudo pip3 install gpiozero
# https://www.digikey.com/en/maker/blogs/2021/how-to-control-servo-motors-with-a-raspberry-pi#:~:text=To%20make%20a%20Raspberry%20Pi,the%20power%20supply%20as%20well.
# https://tutorials-raspberrypi.com/raspberry-pi-servo-motor-control/


sensor1 = 5
sensor2 = 6
sensor3 = 26

ENA = 7
IN1 = 1
IN2 = 16
IN3 = 20
IN4 = 21
ENB = 17

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(sensor1, GPIO.IN)
GPIO.setup(sensor2, GPIO.IN)
GPIO.setup(sensor3, GPIO.IN)

GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(ENB, GPIO.OUT)

# https://www.electronicwings.com/raspberry-pi/raspberry-pi-pwm-generation-using-python-and-c#:~:text=Raspberry%20Pi%20has%20two%20PWM%20channels%20i.e.%20PWM0%20and%20PWM1.&text=The%20PWM%20pins%20on%20Raspberry%20Pi%20are%20shared%20with%20audio%20subsystem.
PENA = GPIO.PWM(ENA, 1000)		#create PWM instance with frequency
PENA.start(0)				#start PWM of required Duty Cycle 
PENB = GPIO.PWM(ENB, 1000)		#create PWM instance with frequency
PENB.start(0)				#start PWM of required Duty Cycle 

GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
GPIO.setup(IN3, GPIO.OUT)
GPIO.setup(IN4, GPIO.OUT)

turning_speed = 0
forward_speed = 20
base_speed = 50

def start():
    GPIO.output(ENA, 0)
    GPIO.output(ENB, 0)

    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1)
    GPIO.output(IN3, 1)
    GPIO.output(IN4, 0)

def stop():
    PENA.ChangeDutyCycle(0)
    PENB.ChangeDutyCycle(0)
    '''
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 0)

    GPIO.output(ENA, 1)
    GPIO.output(ENB, 1)
    '''

def reset():
    PENA.ChangeDutyCycle(100)
    PENB.ChangeDutyCycle(100)
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 0)

    GPIO.output(ENA, 1)
    GPIO.output(ENB, 1)

def Left():
    GPIO.output(IN1, 1)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 1) #1
    GPIO.output(IN4, 0)

def Right():
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1) #1
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)

def Back():
    GPIO.output(IN1, 0)
    GPIO.output(IN2, 1)
    GPIO.output(IN3, 1)
    GPIO.output(IN4, 0)

def Forth():
    GPIO.output(IN1, 1)
    GPIO.output(IN2, 0)
    GPIO.output(IN3, 0)
    GPIO.output(IN4, 1)


i = 0
lineTarget = 4500 # 4500 middle sensor
optiSpd = 40 # 40 50% pulse duration
minSpd = 0
maxSpd = 100
Kp = 0.006 #0.004
Kd = 0.4 # 0.4
Ki = 0.0005 # 0.0005

last_sensor = "first_time"
forth_sensed = False
lSpd, rSpd = (optiSpd, optiSpd)
period_start = time()
period = 0.05 # in seconds 0.05
lastPosition = 0

def initLineFollower():
    global last_sensor, forth_sensed, period_start, lSpd, rSpd, lastPosition, i
    stop()
    last_sensor = "first_time"
    forth_sensed = False
    lSpd, rSpd = (optiSpd, optiSpd)
    period_start = time()
    lastPosition = 0
    i = 0

def readSensors():
    global forth_sensed, last_sensor
    # 0 out of line left
    # 1500 left sensor
    # 3000 between left and middle sensors
    # 4500 middle sensor
    # 6000 between right and middle sensors
    # 7500 right sensor
    # 9000 out of line right
    position = 9000

    sensor1_val = GPIO.input(sensor1)
    sensor2_val = GPIO.input(sensor2)
    sensor3_val = GPIO.input(sensor3)

    if not sensor1_val and not sensor2_val and not sensor3_val:
        if forth_sensed:
            if last_sensor == "left": # 6000 between right and middle sensors
                position = 6000
            elif last_sensor == "right": # 3000 between left and middle sensors
                position = 3000
        elif last_sensor == "right": # 9000 out of line right
            position = 9000
        elif last_sensor == "left": # 0 out of line left
            position = 0
        elif last_sensor == "first_time":
            position = 9000 # 9000 out of line right

    elif sensor1_val and sensor2_val and sensor3_val: # off the ground
        position = 4500 # 4500 center
        forth_sensed = False
        last_sensor = "first_time"

    elif sensor3_val and not sensor2_val and not sensor1_val: # right sensor
        position = 7500 # 7500 right sensor
        forth_sensed = False
        last_sensor = "right"

    elif sensor1_val and not sensor2_val and not sensor3_val: # left sensor
        position = 1500 # 1500 left sensor
        forth_sensed = False
        last_sensor = "left"

    elif sensor2_val and not sensor1_val and not sensor3_val:
        position = 4500 # 4500 middle sensor
        forth_sensed = True

    elif sensor2_val and sensor3_val and not sensor1_val:
        position = 6000 # 6000 between right and middle sensors
        forth_sensed = True

    elif sensor2_val and sensor1_val and not sensor3_val:
        position = 3000 # 3000 between left and middle sensors
        forth_sensed = True

    elif sensor1_val and not sensor2_val and sensor3_val: # this just doesn't happen but just incase
        position = 9000 # 9000 out of line right
        forth_sensed = False

    else: # this just doesn't happen but just incase
        position = 9000 # 9000 out of line right
        forth_sensed = False

    return position

def constrain(speed, minSpeed, maxSpeed):
    if speed > maxSpeed:
        return maxSpeed
    elif speed < minSpeed:
        return minSpeed
    else:
        return speed

def computePID(position):
    global lastPosition, i
    error = position-lineTarget
    p = error
    i = i + error*period
    d = (position-lastPosition) / period
    lastPosition = position
    adjustedValue=(p*Kp + i*Ki + d*Kd)
    lSpd=constrain(optiSpd+adjustedValue,minSpd,maxSpd)
    rSpd=constrain(optiSpd-adjustedValue,minSpd,maxSpd)
    #print(lSpd, rSpd)
    return lSpd, rSpd