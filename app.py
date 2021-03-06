from tkinter import *
from tkinter import ttk
import cv2
import dlib
import pyautogui
from PIL import Image, ImageTk
from point_detection import *
import google_cloud_speech_to_text as text_to_speech
import time
import math

import mediapipe
import cv2
import edwin
import pyautogui

import threading
import os
from pymouse import PyMouse

mouse = PyMouse()

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

isLearning = False
isToggle = True
learnCommandName = ""

pyautogui.PAUSE = 1
resolution = pyautogui.size()
    
def updateGUI(root, panel, frame):
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image = img)
    panel.imgtk = imgtk
    panel.config(image = imgtk)
    root.update()


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
    # frame1 = cv2.resize(frame, (1280, 720))
    # run(frame1)

    key = cv2.waitKey(1) & 0xFF
    return frame1

def recordOnce(hands):
    global isToggle
    ret, frame = cap.read()
    #Unedit the below line if your live feed is produced upsidedown
    #flipped = cv2.flip(frame, flipCode = -1)
    
    #Determines the frame size, 640 x 480 offers a nice balance between speed and accurate identification
    # frame1 = cv2.resize(frame, (1280, 720))
    frame1 = cv2.resize(frame, (640, 480))
    #  when you have to tell them know they have to be late show the(frame1)
    
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
    # cv2.waitKey(1)
    if len(normalizedList) > 0:
        wrist =  {
            'x': normalizedList[8].x,
            'y': normalizedList[8].y,
            'z': normalizedList[8].z,
        }
        if (isToggle):
            hand = (wrist['x'] * resolution[0], wrist['y'] * resolution[1])
            mouse.move(int(resolution[0]-hand[0]), int(hand[1]))
    if (not isToggle):
        run(frame1, mouse)
    return (normalizedList, frame1)

def learnCommand(commandName, btn, hands, root, panel):
    global savedCommands
    global isLearning
    isLearning = True
    currentFrame = []

    commandMap = {
        'click': [[pyautogui.click, []]],
        'scroll': [[pyautogui.press, ['pdgn']]],
        'open-app': [
            [pyautogui.press, ['win']],
        ],
        'open-browser': [
            [pyautogui.press, ['win']],
            [pyautogui.typewrite, ['chrome']],
            [pyautogui.press, ['enter']]
        ],
        'open-url': [
            [pyautogui.press, ['win']],
            [pyautogui.typewrite, ['chrome']],
            [pyautogui.press, ['enter']],
            [pyautogui.hotkey, ['ctrl', 'l']],
        ],
        'open-game': [
            [os.system, ['"D:\\Desktop\\Geometry.Dash.v2.1\\GeometryDash.exe"']],
        ]
    }

    start = time.time()
    tempCommand = {}

    while True:
        (ret, currentFrame) = recordOnce(hands)
        updateGUI(root, panel, currentFrame)
        difference = time.time() - start
        if difference >= 5:
            break
        
        number = math.ceil(5 - difference)
        btn.config(text=f'Capturing start sign in {number} seconds...')

    start = time.time()

    (normalizedList, currentFrame) = recordOnce(hands)
    updateGUI(root, panel, currentFrame)

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

    while True:
        (ret, currentFrame) = recordOnce(hands)
        updateGUI(root, panel, currentFrame)
        difference = time.time() - start
        if difference >= 5:
            break
        
        number = math.ceil(5 - difference)
        btn.config(text=f'Capturing end sign in {number} seconds...')
    
    (normalizedList, currentFrame) = recordOnce(hands)
    updateGUI(root, panel, currentFrame)

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
    tempCommand['combo']['endingSign'] = parseNormalizedList(normalizedList)
    tempCommand['combo']['difference'] = difference

    start = time.time()

    if commandName == 'open-url' or commandName == 'open-app':

        formattedString = ''
        if commandName == 'open-url':
            formattedString = 'URL'
        else:
            formattedString = 'app'

        while True:
            difference = time.time() - start
            if difference >= 5:
                break
            
            number = math.ceil(5 - difference)
            btn.config(text=f'Listening for {formattedString} in {number} seconds...')
            updateGUI(root, panel, displayFrame())
        
        start = time.time()
        URL = text_to_speech.getURL()
        if URL == '':
            while True:
                difference = time.time() - start
                if difference >= 3:
                    break
                
                number = math.ceil(3 - difference)
                btn.config(text=f'Fetching for {formattedString} in {number} seconds...')
                updateGUI(root, panel, displayFrame())
            URL = text_to_speech.getURL()
        commandArray = commandMap[commandName]
        commandArray.append([pyautogui.typewrite, [URL]])
        commandArray.append([pyautogui.press, ['enter']])
        commandMap[commandName] = commandArray
        start = time.time()

    btn.config(text="Finished capturing!")
    start = time.time()

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
    print("Command is")
    print(savedCommands[commandName])

    while time.time() - start < 2:
        pass

    btn.config(text="Looking for a sign...")

def performActions(actions):
    for action in actions:
        fn = action[0]
        fn(*(action[1]))

def textSpeechActivation():
    threading.Thread(target = text_to_speech.main).start()

def main(root):
    pyautogui.moveTo(pyautogui.size()[0]/2, pyautogui.size()[1]/2)

    # Frontend GUI
    panel = ttk.Label(root)  # initialize image panel
    panel.pack(padx=10, pady=10)
    btn = ttk.Label(root, text="Looking for a sign...")
    btn.pack(fill="both", expand=True, padx=10, pady=10)

    learnFrame = LabelFrame(root, text="Learn", padx=5, pady=5)
    learnFrame.pack(side=LEFT, padx=10, pady=10)
    global isLearning

    options = [
        'click',
        'click',
        'open-app',
        'open-browser',
        'open-url',
        'scroll'
    ]
    
    clicked = StringVar()

    clicked.set('right')

    drop = ttk.OptionMenu(learnFrame, clicked, *options).grid(row=0, column=0)

    def learnButtonFn():
        global isLearning
        global learnCommandNameEVOLVES
        learnCommandName = clicked.get()
        isLearning = True
    
    learnClickButton = Button(learnFrame, text="Learn", command=learnButtonFn).grid(row=0, column=1)

    def toggleBtnFn():
        global isToggle
        isToggle = not isToggle
    faceFrame = LabelFrame(root, text="Toggle", padx=5, pady=5)
    faceFrame.pack(side=LEFT, padx=10, pady=10)
    toggleButton = Button(faceFrame, text="Toggle", command=toggleBtnFn).grid(row=0, column=0)

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
            if isLearning:
                timerStart = time.time()
                matchingMode = 0
                learnCommand(learnCommandName, btn, hands, root, panel)
                isLearning = False
                continue

            if matchingMode == 0:
                (normalizedList, currentFrame) = recordOnce(hands)
                timerStart = time.time()
                if len(normalizedList) == 0:
                    updateGUI(root, panel, currentFrame)
                    continue
                startPos = {
                    'x': normalizedList[0].x,
                    'y': normalizedList[0].y,
                    'z': normalizedList[0].z,
                }
                parsedList = parseNormalizedList(normalizedList)
                potentialMatches = edwin.matchInitSign(parsedList, savedCommands)
                if len(potentialMatches) != 0:
                    matchingMode = 1
                    timerStart = time.time()
                    print("Found potential matches")
                    btn.config(text="Please move your hand.")
            elif matchingMode == 1 and time.time() - timerStart >= 1:
                if len(normalizedList) == 0:
                    updateGUI(root, panel, currentFrame)
                    matchingMode = 2
                    timerStart = time.time()
                    btn.config(text="No sign found :(")
                    continue
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
                btn.config(text="Performing action...")
                performActions(actions)
                matchingMode = 2
                timerStart = time.time()
                btn.config(text="Please give us a sign.")
                updateGUI(root, panel, currentFrame)
            elif matchingMode == 1:
                (normalizedList, currentFrame) = recordOnce(hands)
            elif matchingMode == 2 and time.time() - timerStart >= 3:
                matchingMode = 0
                currentFrame = displayFrame()
                btn.config(text="Looking for a sign...")
            else:
                currentFrame = displayFrame()
                
            # Below shows the current frame to the desktop
            # currentImage = cv2.cvtColor(currentFrame, cv2.COLOR_BGR2BGRA)
            updateGUI(root, panel, currentFrame)
            key = cv2.waitKey(1) & 0xFF

            # Below states that if the |q| is press on the keyboard it will stop the system

            if key == ord('q'):
                break

if __name__ == "__main__":
    root = Tk()
    root.title("Tony Stark")
    textSpeechActivation()
    main(root)
    root.mainloop()