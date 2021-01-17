#!/usr/bin/env python3

from config import Config

class Authenticator:
    def __init__(self, config : Config):
        self.config = config
        self.clients = {}
        self.getKnownCreds()

    def getKnownCreds(self):
    	with open(self.config.config['KnownClientsPath']) as f:
    		self.known = f.readlines()
    		for client in self.known:
    			splitted = client.split(":")
    			self.clients[splitted[0]]=splitted[1].strip()
    			
    def authenticate(self, username:str, password:bytes) -> bool:
        return self.clients[username]==password.decode("utf-8")

if __name__=="__main__":
    conf = Config()
    conf.reload()
    auth = Authenticator(conf)
    print(auth.authenticate("admin", b'admin'))
    print(auth.authenticate("admin", b'password'))
