#!/usr/bin/python3
import socket
from protocol import PlayerProtocol

HOST = '127.0.0.1'
PORT =  65000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    #s.sendall(PlayerProtocol.encode(b'hello world xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'))
    testpath = b'/home/weibing/a.mp4'
    s.sendall(PlayerProtocol.encode(testpath))
    data = s.recv(1024)
    print(data)

