from tkinter import *
from tkinter import ttk
import cv2
import dlib
import numpy as np
import pyautogui
from PIL import Image, ImageTk
from point_detection import *
import time
# from threading import TI
# Import the necessary Packages for this software to run

from distutils import command
from lib2to3.pytree import convert
from socket import getservbyname
import mediapipe
import cv2
import edwin
import pyautogui

# Use MediaPipe to draw the hand framework over the top of hands it identifies in Real-Time

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
    
def recordOnce(hands):
    global cap

    (ret, frame) = cap.read()
    frame1 = cv2.resize(frame, (640, 480))
    run(frame1)
    results = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))
    cv2.imshow("Frame", frame1)
    if results.multi_hand_landmarks != None:
        for handLandmarks in results.multi_hand_landmarks:
            drawingModule.draw_landmarks(frame1, handLandmarks, handsModule.HAND_CONNECTIONS)
            normalizedList = []

            for point in handsModule.HandLandmark:
                normalizedLandmark = handLandmarks.landmark[point]
                normalizedList.append(normalizedLandmark)
            
            return normalizedList

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


def main(root):
    # Frontend GUI
    # frontend = ttk.Canvas(root, 800, 800)
    # frontend.grid(row = 0, column = 0)

    # ttk.Label(frontend, text="Welcome to Tony Stark Simulator").grid(column = 0, row = 0)

    # ttk.Button(frontend, text="Start", command=yes).grid(column = 1, row = 1)
    # ttk.Button(frontend, text="Add", command=yes).grid(column = 2, row = 1)
    # ttk.Button(frontend, text="Cancel", command=yes).grid(column = 3, row = 1)
    # ttk.Button(frontend, text="Quit", command=yes).grid(column = 4, row = 1)

    # Flags to help matching
    global savedCommands
    isMatching = False

    # Dictionary of x, y, z for the wrist
    startPos = {} 
    potentialMatches = []
    timerStart = time.time()

    with handsModule.Hands(static_image_mode=False, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as \
        hands:   

        while True:
            recordOnce(hands)
            time.sleep(1)

            # if isMatching and time.time() - timerStart < 5:
            #     continue

            # normalizedList = recordOnce()
            # wrist = {
            #     'x': normalizedList[0].x,
            #     'y': normalizedList[0].y,
            #     'z': normalizedList[0].z
            # }
            # parsedList = parseNormalizedList(normalizedList)

            # if not isMatching:
            #     potentialMatches = edwin.matchInitSign(parsedList, savedCommands)
            #     if len(potentialMatches) != 0:
            #         startPos = wrist
            #         isMatching = True
            #         timerStart = time.time()
            #         print("Found potential matches")
            # else:
            #     endPos = wrist
            #     actions = edwin.matchFinalSign(parsedList, startPos, endPos, potentialMatches, savedCommands)
            #     print(actions)
            #     print("Actions received")
            #     isMatching = False

                    
            #     # Below shows the current frame to the desktop

            #     # TODO Remove
            #     # cv2.imshow('Frame', frame)
            #     # img = Image.fromarray(frame1)
            #     # imgtk = ImageTk.PhotoImage(image = img)
            #     # frontend.create_image(0, 0, anchor=ttk.NW, image=imgtk)
            #     # key = cv2.waitKey(1) & 0xFF

            #     # Below states that if the |q| is press on the keyboard it will stop the system

            #     if key == ord('q'):
            #         break
        
if __name__ == "__main__":
    root = Tk()
    main(root)
    root.mainloop()