#!/usr/bin/env python3

from config import Config


class Authenticator:
    def __init__(self, config : Config):
        self.config = config
        self.clients = {}

    def getKnownCreds(self):
    	with open(self.config['KnownClientsPath']) as f:
    		self.known = f.readlines()
    		for client in self.known:
    			splitted = client.split(:)
    			

    def authenticate(self, username:str, password:BinaryData) -> bool

