import socket
import struct


bridge = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#bridge.connect(('45.80.148.246',1234))
bridge.connect(('localhost',1234))

while True:
    # make the command
    command = input("cmd >") # zaki
    # send the command
    bytestream = struct.pack(f"{len(command)}s",command.encode()) # 5
    #bridge.send(str(struct.calcsize("s")*len(command)).encode()) # 4*5 = 20
    bridge.send(struct.pack("!i",struct.calcsize("s")*len(command)))
    bridge.send(bytestream)
    # receive the response
    size = bridge.recv(4)
    response = bridge.recv(struct.unpack("!i",size)[0])
    unpackedresponse = struct.unpack(f"{round(struct.unpack('!i',size)[0]/struct.calcsize('s'))}s",response)
    print(unpackedresponse[0].decode())
