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

# Use CV2 Functionality to create a Video stream and add some values
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')

"""
What we need
0. Data Structure
    - 1D Array of 21 points, where each point is its location minus the wrist (point 0)
    e.g. [(1, 2, 3), (2, 3, 4), ...]
    
1. Process gestures
    - Give user 5 seconds to make a gesture
    - Save to database 
    - Can do 3 gestures (for now)

2. Match gestures 
    - Take the points on the camera
    - Extract array of 21 points
    - Subtract each corresponding value by the wrist (point 0)
    - Take absolute value of difference
    - Take the maximum of all values
    - Match if smaller than threshold 

Functions to make
    - Normalize hand landmarks position with wrist
        Input: Array of all points
        Output: 1D Array of 21 points
    - Match input to gesture (10% threshold)
        Input: 1D Array of 21 points
        Output: Matched gesture (or null depending on threshold)
    - Record gesture:
        Effect: After 5 seconds, record ONE FRAME that becomes a new gesture,
        which is added to the dictionary/list of gestures

Motion algorithm

Initial dictionary (DATABASE)
{
    $commandName: {
        'combo': {
            'startingSign': [landmarks],
            'endingSign': [landmarks],
            'difference': (x, y),
        }
        'actions': [
            [pyautogui.hotkey, ['win', 'f4]],
            [pyautogui.press, ['ctrl']],
            [...]
        ]
    }
}

Returned dictionary of potential matches
{
    $commandName: {
        'combo': {
            'startingSign': [landmarks],
            'endingSign': [landmarks],
            'difference': (x, y),
            'startPos': (x, y),
        }
        'actions': [
            [pyautogui.hotkey, ['win', 'f4]],
            [pyautogui.press, ['ctrl']],
            [...]
        ]
    }
}

precision movement:
    - only wrist -> hard coded to some fn

Vocabulary

- Position
    - Absolute position of normalized (0 to 1) coordinates on the screen
    - Array 63 values

- Sign
    - Hand position relative to the wrist
    - Position - wrist coordinates
    - aka gesture
    - aka hand sign
    - Array 63 values

- Movement
    - Difference between ending Position and starting Position 
    - Array 63 values

- Precision movement
    - Mode that can be toggled on
    - Moves the mouse according to hand movement

- Combo 
    - (1 starting Sign) -> (1 final sign) & (1 position difference)
    
- Command
    - user defined combo resulting in action

- Action
    - Interaction with the OS with predefined time
    - e.g. [*mouseclick, *hotkeys, *mousemove(x)]

0. Types of Commands
    Right now
    - 1 Combo -> 1 Action (click, scroll, enable/disable)

    In the future
    - User defined Actions
    - Precision movement (continuous action)

1. Record combo

2. Match combo
    1. Continuous polling for sign
    2. Once matched to a sign in the database
    3. Get all combos that start with the current sign
    4. Give delay of 2 seconds
    5. Check if final sign and its position difference matches combos from 3
        - No, it's invalid
        - Yes, it's a defined combo
            - perform corresponding action/s

Functions

1. Feedback loop

2. Get all combos that start with the current sign
    Input: 1 Sign, wrist {x:2, y:4,z:8}
    Output: Dictionary of commands (potential matches)

3. Match final sign + movement
    Input: 1 Sign, wrist {x:2, y:4,z:8}, list of commandNames
    Output: Best match (command)

    3.1 get position difference

"""

"""
Input: A list of 21 Point dictionaries, where 
    Point = {
        x: float,
        y: float,
        z: float
    }
Output: A list of 21 Point dictionaries, where each point has been substracted by the wrist's coordinates
"""
def parseNormalizedList(normalizedList):
    for point in reversed(normalizedList):
        point.x -= normalizedList[0].x
        point.y -= normalizedList[0].y
        point.z -= normalizedList[0].z
    return normalizedList

pyautogui.PAUSE = 0.5

def performAction(gestureNumber):
    actionMap = {
        0: [
            [pyautogui.hotkey, ['pgdn']]
            # [pyautogui.press, ['win']],
            # [pyautogui.typewrite, ['calculator']],
            # [pyautogui.press, ['enter']]
        ],
        1: [
            [pyautogui.press, ['win']],
            [pyautogui.typewrite, ['chrome']],
            [pyautogui.press, ['enter']],
            [pyautogui.hotkey, ['ctrl', 'shift', 'n']],
            [pyautogui.hotkey, ['ctrl', 'l']],
            [pyautogui.press, ['enter']],
        ], 
        2: [
            [pyautogui.hotkey, ['alt', 'f4']]
        ]
    }
    actions = actionMap.get(gestureNumber)
    if actions:
        for action in actions:
            fn = action[0]
            fn(*(action[1]))

def main():
    # Emulate time with counters
    COUNTER_START = 50
    counter = COUNTER_START

    # Dictionary of saved commands
    commands = {} 
    tempCommand = {} # While recording, put first half here

    # Flags to help toggle recording and matching
    isRecording = False
    isMatching = False

    # Dictionary of x, y, z for the wrist
    startPos = {} 
    potentialMatches = []

    with handsModule.Hands(static_image_mode=False,
                       min_detection_confidence=0.7,
                       min_tracking_confidence=0.7, max_num_hands=2) as \
        hands:

        # Create an infinite loop which will produce the live feed to our desktop and that will search for hands

        while True:
            (ret, frame) = cap.read()

            # Unedit the below line if your live feed is produced upsidedown
            # flipped = cv2.flip(frame, flipCode = -1)

            # Determines the frame size, 640 x 480 offers a nice balance between speed and accurate identification

            frame1 = cv2.resize(frame, (640, 480))

            # produces the hand framework overlay ontop of the hand, you can choose the colour here too)

            results = hands.process(cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB))

            # Incase the system sees multiple hands this if statment deals with that and produces another hand overlay

            if results.multi_hand_landmarks != None:
                for handLandmarks in results.multi_hand_landmarks:
                    drawingModule.draw_landmarks(frame1, handLandmarks,
                            handsModule.HAND_CONNECTIONS)

                    # Added Code to find Location of Index Finger !!

                    normalizedList = []

                    for point in handsModule.HandLandmark:

                        normalizedLandmark = handLandmarks.landmark[point]
                        normalizedList.append(normalizedLandmark)

                    wrist = {
                        'x': normalizedList[0].x,
                        'y': normalizedList[0].y,
                        'z': normalizedList[0].z
                    }
                    parsedList = parseNormalizedList(normalizedList)

                    # Record 3 movements first
                    if len(commands) < 3:
                        if counter == 1:
                            # Parse the list with respect to the wrist
                            numCommands = len(commands)

                                
                            # Hardcoded commands order
                            commandName = ''
                            commandActions = []

                            # Determine command name
                            if numCommands == 0:
                                commandName = 'click'
                                commandActions = [[pyautogui.click, []]]
                            elif numCommands == 1:
                                commandName = 'scroll'
                                commandActions = [[pyautogui.press, ['pdgn']]]
                            else:
                                commandName = 'right-click'
                                commandActions = [[pyautogui.click, ['right']]]


                            # Add to commands if recording new, otherwise complete previous one
                            if not isRecording:
                                tempCommand['combo'] = {'startingSign': parsedList}
                                tempCommand['actions']  = commandActions
                                startPos = wrist 
                                print(f"Started recording command {commandName}")
                                print(f"startPos is")
                                print(startPos)
                            else:
                                tempCommand['combo']['endingSign'] = parsedList
                                endPos = wrist
                                difference = {
                                    'x': endPos.get('x') - startPos.get('x'),
                                    'y': endPos.get('y') - startPos.get('y'),
                                    'z': endPos.get('z') - startPos.get('z')
                                } 
                                tempCommand['combo']['difference'] = difference
                                commands[commandName] = {
                                    'combo': {
                                        'startingSign': tempCommand.get('combo').get('startingSign'),
                                        'endingSign': parsedList,
                                        'difference': {
                                            'x': endPos.get('x') - startPos.get('x'),
                                            'y': endPos.get('y') - startPos.get('y'),
                                            'z': endPos.get('z') - startPos.get('z')
                                        }
                                    },
                                    'actions': commandActions
                                }
                                print(f"Finished recording command {commandName}")
                                print("endPos is")
                                print(endPos)
                                print("difference is")
                                print(commands.get(commandName).get('combo').get('difference'))
                            isRecording = not isRecording
                    else:
                        if not isMatching:
                            potentialMatches = edwin.matchInitSign(parsedList, commands)
                            if len(potentialMatches) != 0:
                                counter = COUNTER_START
                                startPos = wrist
                                isMatching = True
                                print("Found potential matches")
                        else:
                            if counter == 1:
                                endPos = wrist
                                actions = edwin.matchFinalSign(parsedList, startPos, endPos, potentialMatches, commands)
                                print(actions)
                                print("Actions received")
                                isMatching = False


                        
            # Below shows the current frame to the desktop

            cv2.imshow('Frame', frame1)
            key = cv2.waitKey(1) & 0xFF

            counter -= 1

            if counter == 0:
                counter = COUNTER_START

            # Below states that if the |q| is press on the keyboard it will stop the system

            if key == ord('q'):
                break

if __name__ == "__main__":
   main() 
