#!env/bin/python

import cv2
import numpy as np
from time import sleep


import threading
import time

bitmap = np.zeros((512,512,3),np.uint8)
def update_bitmap():
    for i in range(512):
        bitmap[i,i,:] = 128
        sleep(1/32)

LDown = False
def mouse_event(event,x,y,flags,param):
    global LDown
    # event:
    # 0 move
    # 1/4 L-down/up
    # 2/5 R-down/up
    # 3/6 x-down/up (scrollwheel button or sidebuttons)
    if event > 0:
        print(event,x,y,flags,param)
        if event == 1:
            LDown = True
        if event == 4:
            LDown = False
    if LDown:
        bitmap[y,x,1] = 255


def main():
    threading.Thread(target=update_bitmap).start()

    hz = 30
    delta_t = 1 / hz
    t = time.time()
    try:
        while True:
            if time.time() > t+delta_t:
                t += delta_t
                cv2.setMouseCallback("fooImage", mouse_event)
                cv2.imshow("fooImage", bitmap)
                cv2.waitKey(1)

    except KeyboardInterrupt:
        cv2.destroyAllWindows()
        exit(0)
