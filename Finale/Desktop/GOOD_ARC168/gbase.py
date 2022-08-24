import pigpio
from time import sleep
import sys

# first type sudo pigpiod
pi = pigpio.pi()       # pi1 accesses the local Pi's GPIO
if not pi.connected:
    print("Not connected to Raspberry Pi ... goodbye.")
    sys.exit()

MOUTH = 12
MOUTH_MIN = 500 # 1500
MOUTH_MAX = 2500 # 1600
MOUTH_REST = 1500
CURRENT_MOUTH = 0.36*(MOUTH_MAX-MOUTH_MIN) + MOUTH_MIN

BOTTOM = 13
BOTTOM_MIN = 500
BOTTOM_MAX = 2500
BOTTOM_REST = 1500
CURRENT_BOTTOM = 1.00*(BOTTOM_MAX-BOTTOM_MIN) + BOTTOM_MIN

TILT = 18
TILT_MIN = 1700
TILT_MAX = 2500
TILT_REST = 2000
CURRENT_TILT = 0.90*(TILT_MAX-TILT_MIN) + TILT_MIN

SPINE = 19
SPINE_MIN = 500
SPINE_MAX = 2000
SPINE_REST = 1000
CURRENT_SPINE = 0.36*(SPINE_MAX-SPINE_MIN) + SPINE_MIN

def turnOffArm():
    pi.set_servo_pulsewidth(MOUTH, 0) #mouth 1500-1600    PWMSoftwareFallback: To reduce servo jitter, use the pigpio pin factory
    pi.set_servo_pulsewidth(BOTTOM, 0) # bottom 500-2500
    pi.set_servo_pulsewidth(TILT, 0) #tilt 1700-2500 range
    pi.set_servo_pulsewidth(SPINE, 0) #spine 500-2000
turnOffArm()

def go_to_coordinates(mode, position, m, b, t, s, step=30, delay=0.02, shape=None): # 0.05
    global CURRENT_MOUTH, CURRENT_BOTTOM, CURRENT_TILT, CURRENT_SPINE

    if mode == "Cargo Pass":
        CURRENT_MOUTH = m
        CURRENT_BOTTOM = b
        CURRENT_TILT = t
        CURRENT_SPINE = s

        pi.set_servo_pulsewidth(MOUTH, CURRENT_MOUTH)
        pi.set_servo_pulsewidth(BOTTOM, CURRENT_BOTTOM)
        pi.set_servo_pulsewidth(TILT, CURRENT_TILT)
        pi.set_servo_pulsewidth(SPINE, CURRENT_SPINE)
        return m!=CURRENT_MOUTH or b!=CURRENT_BOTTOM or t!=CURRENT_TILT or s!=CURRENT_SPINE
    
    if mode == "Arm":
        if shape == "Circles":
            delay = 0.05
            step = 30
            if position == 3:
                delay = 0.02 # 0.05
                step = 80 # 80
            elif position == 4:
                delay = 0.01 # 0.03
                step = 100 # 100

        elif shape == "Squares":
            if position == 3:
                delay = 0.02 # 0.05
                step = 80 # 80
            elif position == 4:
                delay = 0.02 # 0.03
                step = 100 # 100

        elif shape == "Rectangles":
            if position == 3:
                delay = 0.02 # 0.05
                step = 80 # 80
            elif position == 4:
                delay = 0.01 # 0.03
                step = 100 # 100

        elif shape == "Triangles":
            print("oof issa triangle")

    mouth_step = (m - CURRENT_MOUTH) / step
    bottom_step = (b - CURRENT_BOTTOM) / step
    tilt_step = (t - CURRENT_TILT) / step
    spine_step = (s - CURRENT_SPINE) / step

    if m!=CURRENT_MOUTH or b!=CURRENT_BOTTOM or t!=CURRENT_TILT or s!=CURRENT_SPINE:
        #before = millis()
        for i in range(step):
            if CURRENT_MOUTH > 2500:
                CURRENT_MOUTH = 2500
            elif CURRENT_MOUTH < 500 and CURRENT_MOUTH != 0:
                CURRENT_MOUTH = 500

            if CURRENT_BOTTOM > 2500:
                CURRENT_BOTTOM = 2500
            elif CURRENT_BOTTOM < 500 and CURRENT_BOTTOM != 0:
                CURRENT_BOTTOM = 500

            if CURRENT_TILT > 2500:
                CURRENT_TILT = 2500
            elif CURRENT_TILT < 500 and CURRENT_TILT != 0:
                CURRENT_TILT = 500

            if CURRENT_SPINE > 2500:
                CURRENT_SPINE = 2500
            elif CURRENT_SPINE < 500 and CURRENT_SPINE != 0:
                CURRENT_SPINE = 500

            CURRENT_MOUTH += mouth_step
            pi.set_servo_pulsewidth(MOUTH, round(CURRENT_MOUTH))
            CURRENT_BOTTOM += bottom_step
            pi.set_servo_pulsewidth(BOTTOM, round(CURRENT_BOTTOM))
            CURRENT_TILT += tilt_step
            pi.set_servo_pulsewidth(TILT, round(CURRENT_TILT))
            CURRENT_SPINE += spine_step
            pi.set_servo_pulsewidth(SPINE, round(CURRENT_SPINE))
            sleep(delay)

        CURRENT_MOUTH = m
        CURRENT_BOTTOM = b
        CURRENT_TILT = t
        CURRENT_SPINE = s
        print("done doing move at position", position)

    pi.set_servo_pulsewidth(MOUTH, CURRENT_MOUTH)
    pi.set_servo_pulsewidth(BOTTOM, CURRENT_BOTTOM)
    pi.set_servo_pulsewidth(TILT, CURRENT_TILT)
    pi.set_servo_pulsewidth(SPINE, CURRENT_SPINE)

    return m!=CURRENT_MOUTH or b!=CURRENT_BOTTOM or t!=CURRENT_TILT or s!=CURRENT_SPINE
