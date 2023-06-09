import socket
import struct
import threading
import pickle

MASTER = None
CLIENTS = []


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


def HandleMaster(cli):
    while True:
        command = receive(cli)
        for slave in CLIENTS:
            send(command, slave)


def HandleClient(cli):
    while True:
        send(receive(cli), MASTER)


bridge = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
bridge.bind(("localhost", 9999))
bridge.listen(socket.SOMAXCONN)


while True:
    cli_, addr = bridge.accept()
    if cli_.recv(1024).decode() == "master":
        MASTER = cli_
        threading.Thread(target=HandleMaster, args=(MASTER,)).start()
        print("Master Connected!")
    else:
        CLIENTS.append(cli_)
        threading.Thread(target=HandleClient, args=(cli_,)).start()
        print("Client Connected!")
