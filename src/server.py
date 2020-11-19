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

from session import Session
from config import Config
from aux import MQTTError

class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket,shared, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.csocket = clientsocket
        self.clientAddress = clientAddress
        self.shared = shared
        logging.info("New connection added: {}".format(clientAddress))
    def run(self):
        sess = Session()
        logging.info("Connection from :{} ".format(clientAddress))
        msg = ''

        while True:
            if running:
                r, _, _ = select.select([self.csocket], [], [], 1)
                if r:
                    data = self.csocket.recv(self.shared['config'].config['MaxPacketSize'])
                    sess.registerNewData(data)
                    try:
                        packet = sess.classifyData()
                        response = sess.handleConnection(packet)
                        
                    except MQTTError:
                        msg='bye'

                    if msg=='bye':
                        logging.warning("Client at {} disconnected...".format(self.clientAddress))
                        self.csocket.close()
                        break
                else:
                    self.csocket.close()
                    break
                print ("from client", msg)
                self.csocket.send(response.data)
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
config = Config()
shared = {}
shared['config'] = config
running = True
while True:
    server.listen(1)
    try:
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock, shared)
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


