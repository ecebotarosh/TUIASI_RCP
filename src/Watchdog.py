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
    
    def getUsedLogins(self) -> list:
        for connection in self.threads:

