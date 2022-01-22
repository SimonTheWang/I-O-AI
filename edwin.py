import math

def matchSign(inputSign, savedSign):
    # Array holding difference of each point
    differenceMetrics = []
    
    i = 0
    # Loop through landmarks of savedSign
    for landmark in savedSign:
        x = abs(landmark.x - inputSign[i].x)
        y = abs(landmark.y - inputSign[i].y)
        z = abs(landmark.z - inputSign[i].z)

        # Reject if over threshold
        if x+y+z >= 0.1:
            # gesture rejected
            return False
        
        i += 1
    return True

"""
    2. Get all combos that start with the current sign
        Input: 1 Sign
        Output: List of potential matches (command strings)
"""
def matchInitSign(inputSign, commands):
    potentialMatches = []
    for commandName, command in commands.items():
        if matchSign(inputSign, command.get('combo').get('startingSign')):
            potentialMatches.append(commandName)
    return potentialMatches

"""
    3. Match final sign + movement
        Input: 1 Sign, wrist x, wrist y, dictionary of possible matches
        Output: Best match (command)

        3.1 get position difference
"""
def getPosThreshold(initCoord, endCoord, expectedDiff):
    relativeDiff = 0
    for coord in endCoord:
        relativeDiff += abs((endCoord.get(coord)-initCoord.get(coord))-expectedDiff.get(coord))
    return relativeDiff

def matchFinalSign(inputSign, initWrist, finalWrist, matchList, commands):
    for commandName, command in commands.items():
        if commandName in matchList:
            combo = command.get('combo')
            actions = command.get('actions')
            if matchSign(inputSign, combo.get('endingSign')):
                posDiff = getPosThreshold(initWrist, finalWrist, combo.get('difference'))
                if posDiff <= 0.2:
                    return actions
                    
    return []


"""
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
"""