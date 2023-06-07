import socket
import pickle
import struct


bridge = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
bridge.bind(("localhost",9999))
bridge.listen(2)
master,_ = bridge.accept()
print("master connected!")
slave,_ = bridge.accept()
print("slave connected!")
slave.send(master.recv(1024))

payload_size = struct.calcsize('>L')
data = b""

while True:
    while len(data) < payload_size:
        received = slave.recv(4096)
        data += received
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack('>L',packed_msg_size)[0]
    while len(data) < msg_size:
        data += slave.recv(4096)
    
    frame_data = data[:msg_size]
    data = data[msg_size:]


    size = len(frame_data)
    master.sendall(struct.pack('>L',size)+frame_data)


