import socket


client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(('localhost',9999))

datasize = int(client.recv(1024).decode())

chunk = 1024

data = b''

while len(data) < datasize:
    data += client.recv(chunk)

with open("photo.jpg","wb") as f:
    f.write(data)
    
