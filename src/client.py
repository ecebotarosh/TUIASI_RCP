#!/usr/bin/env python3
import socket
import os
from dotenv import load_dotenv

load_dotenv()
SERVER = os.getenv("IP")
PORT = int(os.getenv("PORT"))
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))
client.sendall(b'\x10\xa4\x02\x00\x04MQTT\x05\xfe\x01\xff[\x11\x00\x00\x00\x02!\x00\x02&\x00\x05salut\x00\x04Emil&\x00\x05salut\x00\x08bunaziua&\x00\x05hello\x00\x07welcome\x15\x00\x08userpass\x16\x00\x04\x02\x03\x04\x05&\x00\x05salut\x00\x06Andrei\x00\x0er3allyrandomid;\x18\x00\x00\x00#\x01\x01\x02\x00\x00\x00 &\x00\x0esalut_din_will\x00\x03dev\x03\x00\x11application/x-pdf\t\x00\x02\x04\x08\x00\x07pc/temp\x00Vthis is a test message to be sent as a will payload and be submitted as key-value pair\x00\x05admin\x00\x08password')
while True:
    in_data = client.recv(1024)
    print("From Server :", in_data.decode())
    out_data = input()
    client.sendall(bytes(out_data, 'UTF-8'))
    if out_data == 'bye':
        break
client.close()
