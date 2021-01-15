#!/usr/bin/env python3

import struct
from MQTTPacket import MQTTPacket
from ConnectPacket import ConnectPacket
from ConnackPacket import ConnackPacket
from aux import MQTTError
from config import Config

class Session:
    def __init__(self):
        self.data = b""
        self.topics = []
        self.will = ""
        self.config = Config()
        self.config.reload()

    def reset(self):
        self.data=b""
        self.topics = []
        self.will = ""
        self.config = Config()
        self.config.reload()

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
            packet.parseFixedHeader()
            packet.parseVariableHeader()
            packet.parsePayloadHeader()
            print(packet.fixed)
            print(packet.variable)
            print(packet.payload)
            if packet.variable['cleanStart']:
                self.reset()
            #if not self.config['AllowPublicAccess']:
            #    if packet.fixed['usernameFlag'] and packet.fixed['passwordFlag']:
            #       if authen
            return ConnackPacket(ConnackPacket.generatePacketData(False, 0x00, {'SessionExpiryInterval': 30}))


if __name__ == "__main__":
    byte_data = b"\x10\x0f\x15\x30"
    data = struct.pack(">{}s".format(len(byte_data)), byte_data)
    session = Session(data)
    packet = session.classifyData()
    packet.parseFixedHeader()
