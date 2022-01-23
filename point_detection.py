import cv2
import dlib
import numpy as np
import pyautogui
import time

fname = './models/shape_predictor_68_face_landmarks_GTX.dat'
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(fname)
previous_nose = None
previous_mouse = None
og_nose = None

def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype = dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def measureHead(frame):
    global fname
    global detector
    global predictor
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)
        for (x, y) in shape:
            cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
        nose = (shape[30][0], shape[30][1])
        return nose
    return None

def run(frame, hand):
    global og_nose
    pyautogui.FAILSAFE = False
    (maxScreenX, maxScreenY) = pyautogui.size()
    (oldMouseX, oldMouseY) = pyautogui.position()
    oldMouseX = maxScreenX - oldMouseX
    baseMoveX = maxScreenX/maxScreenX
    baseMoveY = maxScreenY/maxScreenY

    positionDiff = [0,0] #(x,y)
    # calcultate change in nose position stored in diffIndex
    
    nose = (hand['x']*maxScreenX,hand['y']*maxScreenY)
    print(nose)
    # nose = measureHead(frame)

    if og_nose is None:
        og_nose = nose
    if nose is None:
        print('no nose found')
    else:
        positionDiff[0] = nose[0] - og_nose[0]
        positionDiff[1] = nose[1] - og_nose[1] 

        (newXCoord, newYCoord) = (oldMouseX, oldMouseY) 

        if abs(positionDiff[0]) > 10:
            print('xOffset: ', positionDiff[0] * baseMoveX)
            newXCoord = positionDiff[0] * baseMoveX + oldMouseX
            if newXCoord >= maxScreenX: 
                newXCoord = maxScreenX-1
            elif newXCoord <= 0:
                newXCoord = 1
        if abs(positionDiff[1]) > 10:
            print('yOffset: ', positionDiff[1] * baseMoveY)
            newYCoord = positionDiff[1] * baseMoveY + oldMouseY
            if newYCoord >= maxScreenY: 
                newYCoord = maxScreenY-1
            elif newYCoord <= 0:
                newYCoord = 1
            
        pyautogui.moveTo(maxScreenX-nose[0], nose[1])
        # pyautogui.moveTo(maxScreenX-int(newXCoord), int(newYCoord))
        # time.sleep(.1)