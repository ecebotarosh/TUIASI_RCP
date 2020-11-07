#!/usr/bin/env python3
import socket
import os
from dotenv import load_dotenv

load_dotenv()
SERVER = os.getenv("IP")
PORT = os.getenv("PORT")
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(bytes("This is from Client", 'UTF-8'))
while True:
    in_data = client.recv(1024)
    print("From Server :", in_data.decode())
    out_data = input()
    client.sendall(bytes(out_data, 'UTF-8'))
    if out_data == 'bye':
        break
client.close()
