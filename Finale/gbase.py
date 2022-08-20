import pigpio
from time import sleep

# first type sudo pigpiod
pi = pigpio.pi()       # pi1 accesses the local Pi's GPIO

MOUTH = 12
MOUTH_MIN = 1500
MOUTH_MAX = 1600
MOUTH_REST = 1500
CURRENT_MOUTH = MOUTH_REST

BOTTOM = 13
BOTTOM_MIN = 500
BOTTOM_MAX = 2500
BOTTOM_REST = 1500
CURRENT_BOTTOM = BOTTOM_REST

TILT = 18
TILT_MIN = 1700
TILT_MAX = 2500
TILT_REST = 2000
CURRENT_TILT = TILT_REST

SPINE = 19
SPINE_MIN = 500
SPINE_MAX = 2000
SPINE_REST = 1000
CURRENT_SPINE = SPINE_REST


pi.set_servo_pulsewidth(MOUTH, 0) #mouth 1500-1600    PWMSoftwareFallback: To reduce servo jitter, use the pigpio pin factory
pi.set_servo_pulsewidth(BOTTOM, 0) # bottom 500-2500
pi.set_servo_pulsewidth(TILT, 0) #tilt 1700-2500 range
pi.set_servo_pulsewidth(SPINE, 0) #spine 500-2000

def go_to_coordinates(m, b, t, s, step=10, delay=0.03):
    global CURRENT_MOUTH, CURRENT_BOTTOM, CURRENT_TILT, CURRENT_SPINE

    mouth_step = (m - CURRENT_MOUTH) / step
    bottom_step = (b - CURRENT_BOTTOM) / step
    tilt_step = (t - CURRENT_TILT) / step
    spine_step = (s - CURRENT_SPINE) / step

    #before = millis()
    for i in range(step):
        CURRENT_MOUTH += mouth_step
        pi.set_servo_pulsewidth(MOUTH, CURRENT_MOUTH)
        CURRENT_BOTTOM += bottom_step
        pi.set_servo_pulsewidth(BOTTOM, CURRENT_BOTTOM)
        CURRENT_TILT += tilt_step
        pi.set_servo_pulsewidth(TILT, CURRENT_TILT)
        CURRENT_SPINE += spine_step
        pi.set_servo_pulsewidth(SPINE, CURRENT_SPINE)
        sleep(delay)

    CURRENT_MOUTH = m
    CURRENT_BOTTOM = b
    CURRENT_TILT = t
    CURRENT_SPINE = s
  
    pi.set_servo_pulsewidth(MOUTH, CURRENT_MOUTH)
    pi.set_servo_pulsewidth(BOTTOM, CURRENT_BOTTOM)
    pi.set_servo_pulsewidth(TILT, CURRENT_TILT)
    pi.set_servo_pulsewidth(SPINE, CURRENT_SPINE)
