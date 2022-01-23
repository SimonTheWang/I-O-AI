import cv2
import dlib
import numpy as np
import pyautogui

fname = './models/shape_predictor_68_face_landmarks.dat'
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(fname)
previous = None


def shape_to_np(shape, dtype="int"):
    coords = np.zeros((68, 2), dtype = dtype)
    for i in range(0, 68):
        coords[i] = (shape.part(i).x, shape.part(i).y)
    return coords

def run(frame):
    global fname
    global detector
    global predictor
    global previous

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 1)
    for rect in rects:
        shape = predictor(gray, rect)
        shape = shape_to_np(shape)

        for (x, y) in shape:
            cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)
        nose = (shape[30][0], shape[30][1])
        topLeft = (shape[39][0], shape[29][1] + 7)
        topRight = (shape[42][0], 0)
        bottom = (0, shape[33][1] - 10)

        scaled_x = pyautogui.size()[0] / ((topRight[0] - topLeft[0]) * (nose[0] - topLeft[0]))
        scaled_y = pyautogui.size()[1] / ((bottom[1] - topLeft[1]) * (nose[1] - topLeft[1]))

        if (previous == None):
            previous = nose
        cv2.rectangle(frame, (topLeft[0], topLeft[1]), (topRight[0], bottom[1]), (255, 0, 0), 1)

        if (pyautogui.size()[0] - scaled_x > 0 and pyautogui.size()[0] - scaled_x < pyautogui.size()[0]) and (scaled_y > 0 and scaled_y <= pyautogui.size()[1]):
            if abs(previous[0] - nose[0]) > 2 or abs(previous[1] - nose[1]) > 2:
                # print(str(pyautogui.size()[0] - scaled_x) + " " + str(scaled_y))
                pyautogui.moveTo(int(pyautogui.size()[0] - scaled_x), int(scaled_y))
                previous = nose