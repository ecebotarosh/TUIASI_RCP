#!/usr/bin/env python3
from os import path

CONFIG_PATH = '../config/srv.conf'
KNOWN_AUTH_METHODS = ['userpass']
KNOWN_CONF_STRINGS = ['AllowPublicAccess', 'AuthenticationMethods', 'KnownClientsPath', 'HistoryMessageQueueSize', 'RetainedMessagesPath', 'DefaultKeepAlive', 'TopicHierarchyListPath', 'MaxPacketSize', 'MaxQoS1QueueSize', 'MaxQoS2QueueSize','MaxSupportedTopics','SessionsPath', 'AllowWildcard', 'KnownTopicsPath']



class Config:
    def __init__(self):
        self.config={'AllowPublicAccess':True, 'AuthenticationMethods':[], 'KnownClientsPath':"", 'HistoryMessageQueueSize':10,'RetainedMessagesPath':"", 'DefaultKeepAlive':60, 'MaxPacketSize':268435456, 'MaxQoS1QueueSize':15, 'MaxQoS2QueueSize':15, 'MaxSupportedTopics':30, 'SessionsPath':"", 'AllowWildcard':False, 'KnownTopicsPath':""}

    def __str__(self):
        return str(self.config)

    def __repr__(self):
        return str(self.config)

    @staticmethod
    def parseConfString(conf_string : str, value:str) -> object:
        if conf_string == "AllowPublicAccess":
            if value=="yes":
                return True
            elif value=="no":
                return False
            else:
                raise ValueError("Unknown value :{} for AllowPublicAccess".format(value.strip()))
        elif conf_string == "AuthenticationMethods":
            values = value.split(",")
            result = list()
            for value in values:
                if value in KNOWN_AUTH_METHODS:
                    result.append(value)
                else:
                    raise ValueError("Unknown value :{} for AuthenticationMethods".format(value.strip()))
            result = list(set(result))
            return result
        elif conf_string=="KnownClientsPath":
            if path.exists(value):
                return value
            raise FileNotFoundError("Unknown filepath :{} for KnownClientsPath".format(value))
        elif conf_string=="HistoryMessageQueueSize":
            return int(value)   
        elif conf_string=="RetainedMessagesPath":
            if path.exists(value):
                return value
            raise FileNotFoundError("Unknown filepath :{} for RetainedMessagesPath".format(value))
        elif conf_string=="DefaultKeepAlive":
            return int(value)
        elif conf_string=="MaxPacketSize":
            return int(value)
        elif conf_string=="MaxQoS1QueueSize":
            return int(value)
        elif conf_string=="MaxQoS2QueueSize":
            return int(value)
        elif conf_string=="MaxSupportedTopics":
            return int(value)
        elif conf_string=="SessionsPath":
            if path.exists(value):
                return value
            raise FileNotFoundError("Unknown filepath :{} for SessionsPath".format(value))
        elif conf_string=="KnownTopicsPath":
            if path.exists(value):
                return value
            raise FileNotFoundError("Unknown filepath :{} for KnownTopicsPath".format(value))
        elif conf_string=="AllowWildcard":
            if value=="yes":
                return True
            elif value=="no":
                return False
            else:
                raise ValueError("Unsupported option : {} for AllowWildcard".format(value))


    def reload(self):
        with open(CONFIG_PATH, 'r') as f:
            conf_lines = f.readlines()

        for line in conf_lines:
            line = line.strip()
            if len(line)!=0:
                conf_string, value = line.split()
                if conf_string in KNOWN_CONF_STRINGS:
                    self.config[conf_string.strip()]=Config.parseConfString(conf_string.strip(), value.strip())

        
if __name__=="__main__":
    config = Config()
    config.reload()
