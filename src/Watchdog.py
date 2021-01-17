#!/usr/bin/env python3


class Watchdog:
    def __init__(self, threads: list):
        self.threads = threads

    def purgeThreadBySocket(self, sock):
        for connection in self.threads:
            if connection.csocket == sock:
                sock.close()
                connection.join()
                self.threads.remove(connection)
    
    def getUsedClientIDs(self, sock) -> list:
        logins = []
        for connection in self.threads:
            if connection.session.clientID not in logins and connection.csocket != sock:
                logins.append(connection.session.clientID)
        return logins

    def getSubscriberSockets(self, sub_topic:str, sock) -> list:
        subscribers = []
        for connection in self.threads:
            if sub_topic in connection.session.topics and connection.csocket!=sock:
                subscribers.append(connection.csocket)
        return subscribers


    def isUsedClientID(self, clientID:str, sock) -> bool
        clientIDs = self.getUsedClientIDs(sock)
        return clientID in clientIDs

    def broadcast(self, msg:bytes, sock) -> None:
        for connection in self.threads:
            if connection.csocket != sock:
                connection.csocket.send(msg)

    def broadcastByTopic(self, msg:bytes, topic:str, sock) -> None:
        for connection in self.threads:
            if topic in connection.sess.topics and sock!=connection.csocket:
                connection.csocket.send(msg)
