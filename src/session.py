#!/usr/bin/env python3

import struct
from MQTTPacket import MQTTPacket
from ConnectPacket import ConnectPacket
from ConnackPacket import ConnackPacket
from aux import MQTTError
from config import Config
from authenticator import Authenticator
from Watchdog import Watchdog

class Session:
    def __init__(self, watchdog, sock):
        self.data = b""
        self.topics = []
        self.will = ""
        self.clientID = ""
        self.config = Config()
        self.config.reload()
        self.auth = Authenticator(self.config)
        self.watchdog = watchdog
        self.socket = sock

    def reset(self):
        self.data=b""
        self.topics = []
        self.will = ""
        self.clientID = ""
        self.username = ""
        self.config = Config()
        self.config.reload()
        self.auth = Authenticator(self.config)

    def registerNewData(self, data: bytes):
        self.data = data

    def classifyData(self) -> MQTTPacket:
        ptype = self.data[0] // 16
        if ptype == 1:
            print("Returning ConnectPacket")
            return ConnectPacket(self.data)
        elif ptype == 2:
            raise MQTTError("Connack Packets should not be parsed by server")
        elif ptype == 3:
            return PublishPacket(self.data)
        elif ptype == 4:
            return PubackPacket(self.data)
        elif ptype == 5:
            return PubrecPacket(self.data)
        elif ptype == 6:
            return PubrelPacket(self.data)
        elif ptype == 7:
            return PubcompPacket(self.data)
        elif ptype == 8:
            return SubscribePacket(self.data)
        elif ptype == 9:
            return SubackPacket(self.data)
        elif ptype == 10:
            return UnsubscribePacket(self.data)
        elif ptype == 11:
            return UnsubackPacket(self.data)
        elif ptype == 12:
            return PingReqPacket(self.data)
        elif ptype == 13:
            return PingResPacket(self.data)
        elif ptype == 14:
            return DisconnectPacket(self.data)
        elif ptype == 15:
            return AuthPacket(self.data)
            raise MQTTError("Not properly implemented yet")


            

    def handleConnection(self, packet: MQTTPacket) -> MQTTPacket:
        if isinstance(packet, ConnectPacket):
            packet.parse()
            print(packet.fixed)
            print(packet.variable)
            print(packet.payload)
            if packet.variable['cleanStart']:
                self.reset()
            if not self.config['AllowPublicAccess']:
                if packet.fixed['usernameFlag'] and packet.fixed['passwordFlag']:
                    if self.auth.authenticate(packet.payload['username'], packet.payload['password']):
                        self.clientID = packet.payload['clientID']
                        return ConnackPacket(ConnackPacket.generatePacketData(False, 0x00, {'SessionExpiryInterval': 0}))
                    else:
                        return ConnackPacket(ConnackPacket.generatePacketData(False, 0x04, {'SessionExpiryInterval': 0}))
            else:
                if self.watchdog.isUsedClientID(packet.payload['clientID']):
                    return ConnackPacket(ConnackPacket.generatePacketData(False, 0x03, {'SessionExpiryInterval':0}))
        elif isinstance(packet, PublishPacket):
            packet.parse()
            subscribers = self.watchdog.getSubscriberSockets(packet.variable['topicName'], self.sock)
            self.watchdog.broadcastByTopic(packet, self.sock)

            if packet.fixed['QoS']==1:
                if subscribers==[]:
                    return PubackPacket(PubackPacket.generatePacketData(packet.variable['packetIdentifier'], 0x10, [])
                else:
                    return PubackPacket(PubackPacket.generatePacketData(packet.variable['packetIdentifier'], 0x00, [])
            elif packet.fixed['QoS']==2:
                if subscribers==[]:
                    return PubrecPacket(PubrecPacket.generatePacketData(packet.variable['packet_id'], 0x10, "No subscribers", {})
                else:
                    return PubrecPacket(PubrecPacket.generatePacketData(packet.variable['packet_id'], 0x00, "SUCCESS", {}
            else:
                return packet
        
            
                
                
                

if __name__ == "__main__":
    byte_data = b"\x10\x0f\x15\x30"
    data = struct.pack(">{}s".format(len(byte_data)), byte_data)
    session = Session(data)
    packet = session.classifyData()
    packet.parseFixedHeader()
