from tkinter import *
from tkinter import ttk
import cv2
import dlib
import numpy as np
import pyautogui
from PIL import Image, ImageTk
from point_detection import *
import time

from distutils import command
from lib2to3.pytree import convert
from socket import getservbyname
import mediapipe
import cv2
import edwin
import pyautogui

drawingModule = mediapipe.solutions.drawing_utils
handsModule = mediapipe.solutions.hands

fname = './models/shape_predictor_68_face_landmarks.dat'
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(fname)
previous = None

# Use CV2 Functionality to create a Video stream and add some values
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

savedCommands = {}
    
def parseNormalizedList(normalizedList):
    for point in reversed(normalizedList):
        point.x -= normalizedList[0].x
        point.y -= normalizedList[0].y
        point.z -= normalizedList[0].z
    return normalizedList

def displayFrame(frameArg=None):
    global cap
    (ret, frame) = cap.read()
    if frameArg:
        frame = frameArg
    frame1 = cv2.resize(frame, (640, 480))
    run(frame1)
    cv2.imshow('Frame', frame1)
    key = cv2.waitKey(1) & 0xFF
    return frame1

def recordOnce(hands):
    ret, frame = cap.read()
    #Unedit the below line if your live feed is produced upsidedown
    #flipped = cv2.flip(frame, flipCode = -1)
    
    #Determines the frame size, 640 x 480 offers a nice balance between speed and accurate identification
    frame1 = cv2.resize(frame, (640, 480))
    run(frame1)
    
    #produces the hand framework overlay ontop of the hand, you can choose the colour here too)
    results = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))

    normalizedList = []
    
    #Incase the system sees multiple hands this if statment deals with that and produces another hand overlay
    if results.multi_hand_landmarks != None:
        for handLandmarks in results.multi_hand_landmarks:
            drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)

            for point in handsModule.HandLandmark:
                normalizedLandmark = handLandmarks.landmark[point]
                normalizedList.append(normalizedLandmark)
    
    #Below shows the current frame to the desktop 
    print(normalizedList)
    # cv2.waitKey(1)
    return (normalizedList, frame1)

def learnCommand(commandName):
    global savedCommands
    commandMap = {
        'click': [[pyautogui.click, []]],
        'scroll': [[pyautogui.press, ['pdgn']]],
        'right': [[pyautogui.click, ['right']]]
    }

    start = time.time()
    tempCommand = {}

    normalizedList = recordOnce()
    startPos = {
        'x': normalizedList[0].x,
        'y': normalizedList[0].y,
        'z': normalizedList[0].z
    }

    tempCommand['combo'] = {'startingSign': parseNormalizedList(normalizedList)}

    # Debug information
    print(f"Started recording command {commandName}")
    print(f"startPos is")
    print(startPos)

    while time.time() - start < 5:
        pass

    normalizedList = recordOnce()

    tempCommand['combo']['endingSign'] = parseNormalizedList(normalizedList)
    endPos = {
        'x': normalizedList[0].x,
        'y': normalizedList[0].y,
        'z': normalizedList[0].z
    }
    difference = {
        'x': endPos.get('x') - startPos.get('x'),
        'y': endPos.get('y') - startPos.get('y'),
        'z': endPos.get('z') - startPos.get('z')
    } 
    tempCommand['combo']['difference'] = difference

    savedCommands[commandName] = {
        'combo': {
            'startingSign': tempCommand.get('combo').get('startingSign'),
            'endingSign': tempCommand.get('combo').get('endingSign'),
            'difference': {
                'x': endPos.get('x') - startPos.get('x'),
                'y': endPos.get('y') - startPos.get('y'),
                'z': endPos.get('z') - startPos.get('z')
            }
        },
        'actions': commandMap.get(commandName)
    }

    # Debug information
    print(f"Finished recording command {commandName}")
    print("endPos is")
    print(endPos)
    print("difference is")
    print(savedCommands.get(commandName).get('combo').get('difference'))

def performActions(actions):
    for action in actions:
        fn = action[0]
        fn(*(action[1]))

def main(root):
    # Frontend GUI
    panel = ttk.Label(root)  # initialize image panel
    panel.pack(padx=10, pady=10)
    btn = ttk.Button(root, text="Snapshot!")
    btn.pack(fill="both", expand=True, padx=10, pady=10)

    # ttk.Button(frontend, text="Start", command=yes).grid(column = 1, row = 1)
    # ttk.Button(frontend, text="Add", command=yes).grid(column = 2, row = 1)
    # ttk.Button(frontend, text="Cancel", command=yes).grid(column = 3, row = 1)
    # ttk.Button(frontend, text="Quit", command=yes).grid(column = 4, row = 1)

    # Flags to help matching    
    global savedCommands
    matchingMode = 0

    # Dictionary of x, y, z for the wrist
    startPos = {} 
    potentialMatches = []
    timerStart = time.time()

    with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:
        currentFrame = []
        while True:
            if matchingMode == 0:
                (normalizedList, currentFrame) = recordOnce(hands)
                parsedList = parseNormalizedList(normalizedList)
                potentialMatches = edwin.matchInitSign(parsedList, savedCommands)
                if len(potentialMatches) != 0:
                    startPos = {
                        'x': normalizedList[0].x,
                        'y': normalizedList[0].y,
                        'z': normalizedList[0].z,
                    }
                    matchingMode = 1
                    timerStart = time.time()
                    print("Found potential matches")
            elif matchingMode == 1 and time.time() - timerStart >= 2:
                (normalizedList, currentFrame) = recordOnce(hands)
                endPos = {
                    'x': normalizedList[0].x,
                    'y': normalizedList[0].y,
                    'z': normalizedList[0].z,
                }
                parsedList = parseNormalizedList(normalizedList)
                
                actions = edwin.matchFinalSign(parsedList, startPos, endPos, potentialMatches, savedCommands)
                print(actions)
                print("Actions received")
                matchingMode = 2
                timerStart = time.time()
            elif matchingMode == 2 and time.time() - timerStart >= 3:
                matchingMode = 0
                currentFrame = displayFrame()
            else:
                currentFrame = displayFrame()
                
            # Below shows the current frame to the desktop
            # currentImage = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2BGRA)
            img = Image.fromarray(currentFrame)
            imgtk = ImageTk.PhotoImage(image = img)
            panel.imgtk = imgtk
            panel.config(image = imgtk)
            root.update()
            key = cv2.waitKey(1) & 0xFF

            # Below states that if the |q| is press on the keyboard it will stop the system

            if key == ord('q'):
                break
        
if __name__ == "__main__":
    root = Tk()
    root.title("Tony Stark")
    main(root)
    root.mainloop()