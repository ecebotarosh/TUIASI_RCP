#!/usr/bin/env python3

import socket
import threading
import logging
import select
import sys
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(filename='../logs/server.log', level=logging.DEBUG)


class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.csocket = clientsocket
        self.clientAddress = clientAddress

        logging.info("New connection added: {}".format(clientAddress))
    def run(self):
        logging.info("Connection from :{} ".format(clientAddress))
        msg = ''
        while True:
            if running:
                r, _, _ = select.select([self.csocket], [], [], 1)
                if r:
                    data = self.csocket.recv(2048)
                    msg = data.decode()
                    if msg=='bye':
                        logging.warning("Client at {} disconnected...".format(self.clientAddress))
                        self.csocket.close()
                        break
                else:
                    self.csocket.close()
                    break
                print ("from client", msg)
                self.csocket.send(bytes(msg,'UTF-8'))
            else:
                break
        
        

IP = os.getenv("IP")
PORT = int(os.getenv("PORT"))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((IP, PORT))
print("Server started")
print("Waiting for client request..")
threadPool = []
running = True
while True:
    server.listen(1)
    try:
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        threadPool.append(newthread)
        newthread.start()
    except KeyboardInterrupt:
        running=False
        print("Setting running to False")
        for thread in threadPool:
            print("Proceeding to kill {}".format(thread))
            thread.join()
            print("Thread : {} joined".format(thread.clientAddress))
        break

print("Killing the server process")


