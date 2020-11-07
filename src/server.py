#!/usr/bin/env python3

import socket
import threading
import logging
import sys
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(filename='../logs/server.log', level=logging.DEBUG)


class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.csocket = clientsocket
        logging.info("New connection added: {}".format(clientAddress))
    def run(self):
        logging.info("Connection from :{} ".format(clientAddress))
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            msg = data.decode()
            if msg=='bye':
              break
            print ("from client", msg)
            self.csocket.send(bytes(msg,'UTF-8'))
        logging.warning("Client at {} disconnected...".format(clientAddress))
        sys.exit(0)
        

IP = os.getenv("IP")
PORT = os.getenv("PORT")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP, PORT))
print("Server started")
print("Waiting for client request..")
while True:
    server.listen(1)
    clientsock, clientAddress = server.accept()
    newthread = ClientThread(clientAddress, clientsock)
    newthread.start()

