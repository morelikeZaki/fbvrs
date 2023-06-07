import socket
import pickle
import struct
import cv2
import numpy as np

import pyautogui

def get_frame():
        screen = pyautogui.screenshot()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (1080, 720), interpolation=cv2.INTER_AREA)
        _,frame = cv2.imencode('.jpg',frame,[int(cv2.IMWRITE_JPEG_QUALITY),90])
        return frame


bridge = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
bridge.connect(('45.80.148.246',9999))
bridge.recv(1024)
running = True
while running:
    frame = get_frame()
    data = pickle.dumps(frame,0)
    size = len(data)
    bridge.sendall(struct.pack('>L',size)+data)
