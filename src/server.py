#!/usr/bin/env python3

from aux import MQTTError
from ConnackPacket import ConnackPacket
from config import Config
from session import Session
from Watchdog import Watchdog
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
    def __init__(self, clientAddress, clientsocket, shared, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.csocket = clientsocket
        self.clientAddress = clientAddress
        self.shared = shared
        self.sess = Session(self.shared['watchdog'])
        logging.info("New connection added: {}".format(clientAddress))


    def broadcast(self, msg:bytes) -> None:
        for connection in self.shared['watchdog'].threads:
            if connection.csocket != self.csocket:
                connection.csocket.send(msg)

    def broadcastByTopic(self, msg:bytes, topic:str) -> None:
        for connection in self.shared['watchdog'].threads:
            if topic in connection.sess.topics:
                connection.csocket.send(msg)


    def run(self):
        logging.info("Connection from :{} ".format(clientAddress))
        msg = ''

        while True:
            if running:
                r, _, _ = select.select([self.csocket], [], [], 1)
                if r:
                    data = self.csocket.recv(self.shared['config'].config['MaxPacketSize'])
                    if data:
                        self.sess.registerNewData(data)
                        try:
                            packet = self.sess.classifyData()
                            response = self.sess.handleConnection(packet)
                            self.csocket.send(response.data)
                            print("I just sent him everything I could") 
                        except MQTTError:
                            msg='bye'

                        if msg=='bye':
                            logging.warning("Client at {} disconnected...".format(self.clientAddress))
                            self.csocket.close()
                        break
                    else:
                        if self.session['will']
                        #handle last will

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
watchdog = Watchdog(threadPool)
shared = {}
shared['config'] = config
shared['watchdog'] = watchdog
running = True
while True:
    server.listen(1)
    try:
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock, shared)
        shared['watchdog'].threads.append(newthread)
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


