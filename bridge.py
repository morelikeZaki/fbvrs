import socket
import threading
import struct

clients = []

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(('0.0.0.0',1234))
server.listen(socket.SOMAXCONN)


def removeclient(client):
    if client in clients:
        clients.remove(client)


def clienthandler(client):
    while True:
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
    while True:
        # get size of wanted data
        size = master.recv(1024)
        # get data
        data = master.recv(int(size.decode()))
        # send data to slave
        for slave in clients:
            try:
                slave.send(size)
                slave.send(data)
            except:
                # slave offline
                pass

master,_ = server.accept()
threading.Thread(target=masterhandler).start()
print("master connected!")
while True:
    client,addr = server.accept()
    print("client connected!")
    clients.append(client)
    threading.Thread(target=clienthandler,args=[client]).start()

    