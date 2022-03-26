from time import sleep
from time import monotonic
from os import system
from pyautogui import *

zero = round(monotonic() * 1000)
one = round(monotonic() * 1000)
two = round(monotonic() * 1000)
three = round(monotonic() * 1000)
four = round(monotonic() * 1000)
five = round(monotonic() * 1000)
six = round(monotonic() * 1000)
seven = round(monotonic() * 1000)
eight = round(monotonic() * 1000)
nine = round(monotonic() * 1000)
ten = round(monotonic() * 1000)
A = round(monotonic() * 1000)
B = round(monotonic() * 1000)
C = round(monotonic() * 1000)
D = round(monotonic() * 1000)
E = round(monotonic() * 1000)
F = round(monotonic() * 1000)

anti_fuckup = 400

def toggling_full_screen():
    print('Toggling Full Screen')
    press('f')
    sleep(0.1)

def closing_this_keyboard():
    print('Closing...')
    serial.close()
    quit()

def connecting_huawei():
    print('Connecting Huawei')
    system("start cmd /K b.exe") #/K remains the window, /C executes and dies (popup)
    delay(3)

def rebooting_router():
    print('Rebooting router')
    system("start cmd /C r.exe") #/K remains the window, /C executes and dies (popup)

def control_save():
    print('Save')
    hotkey('ctrl', 's')
    sleep(0.1)

def bad_print_screen():
    print('Screenshot')
    press('prntscrn')
    sleep(0.1)

def turning_screen_off():
    print('Turning Screen Off...')
    system("start cmd /C turnoff.exe") #/K remains the window, /C executes and dies (popup)
    sleep(1)

def undoing():
    print('Undone')
    hotkey('ctrl', 'z')
    sleep(0.1)

def redoing():
    print('Redone')
    hotkey('ctrl', 'shift', 'z')
    sleep(0.1)

def runbox():
    print('RunBox')
    hotkey('win', 'r')
    sleep(0.1)

def copying():
    print('Copied')
    hotkey('ctrl', 'c')
    sleep(0.1)

def tabbing():
    print('Tabbed')
    press('tab')
    sleep(0.1)

def pasting():
    print('Pasted')
    hotkey('ctrl', 'v')
    sleep(0.1)

def deleting():
    print('Deleting')
    press('delete')
    sleep(0.1)

def messenger():
    print('Messenger m8')
    #press('a')
    #typewrite('quick brown fox')
    hotkey('ctrl', 'shift', 'm')
    sleep(0.1)

def snednoodles():
    moveTo(596,873,duration=0.1)
    sleep(0.1)
    click(button='left')
    typewrite('sned nudes')
    sleep(0.05)
    press('enter')




def Perform(button, alt_down, serial):

    global zero, one, two, three, four, five, six, seven, eight, nine, ten, A, B, C, D, E, F
    global anti_fuckup

    if button=='F' and (round(monotonic() * 1000) >= F + anti_fuckup):
        F = round(monotonic() * 1000)
        toggling_full_screen()

    elif button=='E' and (round(monotonic() * 1000) >= E + anti_fuckup):
        E = round(monotonic() * 1000)
        connecting_huawei()

    elif button=='D' and (round(monotonic() * 1000) >= D + anti_fuckup):
        D = round(monotonic() * 1000)
        #closing_this_keyboard()

    elif button=='C' and (round(monotonic() * 1000) >= C + anti_fuckup):
        C = round(monotonic() * 1000)
        rebooting_router()

    elif button=='B' and (round(monotonic() * 1000) >= B + anti_fuckup):
        B = round(monotonic() * 1000)
        control_save()

    elif button=='A' and (round(monotonic() * 1000) >= A + anti_fuckup):
        A = round(monotonic() * 1000)
        bad_print_screen()
        pass

    elif button=='9' and (round(monotonic() * 1000) >= nine + anti_fuckup):
        nine = round(monotonic() * 1000)
        pass

    elif button=='8' and (round(monotonic() * 1000) >= eight + anti_fuckup):
        eight = round(monotonic() * 1000)
        turning_screen_off()

    elif button=='7' and (round(monotonic() * 1000) >= seven + anti_fuckup):
        seven = round(monotonic() * 1000)
        undoing()

    elif button=='6' and (round(monotonic() * 1000) >= six + anti_fuckup):
        six = round(monotonic() * 1000)
        redoing()

    elif button=='5' and (round(monotonic() * 1000) >= five + anti_fuckup):
        five = round(monotonic() * 1000)
        runbox()

    elif button=='4' and (round(monotonic() * 1000) >= four + anti_fuckup):
        four = round(monotonic() * 1000)
        print('sned noodles')
        snednoodles()


    elif button=='3' and (round(monotonic() * 1000) >= three + anti_fuckup):
        three = round(monotonic() * 1000)
        copying()

    elif button=='2' and (round(monotonic() * 1000) >= two + anti_fuckup):
        two = round(monotonic() * 1000)
        pasting()

    elif button=='1' and (round(monotonic() * 1000) >= one + anti_fuckup):
        one = round(monotonic() * 1000)
        messenger()

    elif button=='0' and (round(monotonic() * 1000) >= zero + anti_fuckup):
        zero = round(monotonic() * 1000)
        pass

    return alt_down, serial


'''
not used
'''

'''
if alt_down:
    tabbing()
'''
'''
if alt_down:
    print('Alt Set To False')
    alt_down = False
    keyUp('alt')
else:
    print('Alt Set To True')
    alt_down = True
    keyDown('alt')
sleep(0.1)
'''
