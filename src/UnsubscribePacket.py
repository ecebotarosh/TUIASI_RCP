#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import VariableByte, MQTTError, CustomUTF8, BinaryData, readCustomUTF8String


class UnsubscribePacket(MQTTPacket):
    def __init__(self, data):
        self.data = data
        self.fixed = {}
        self.fixed_size = 0
        self.variable = {}
        self.variable_size = 0
        self.payload = {}
        self.payload_size = 0

    def parseVariableHeader(self):
        variableHeader = self.data[self.fixed_size:]
        self.variable['packet_id'] = struct.unpack("!H", variableHeader[:2])[0]
        variableHeader = variableHeader[2:]

        # 2 bytes so far

        properties = variableHeader
        num = b""
        for byte in properties:
            num += struct.pack("!B", byte)
            if byte < 0x80:
                break
        required = len(num)

        self.variable['propertyLength'] = struct.unpack(
            "!{}s".format(required), num)[0]
        self.variable['propertyLength'] = VariableByte.decode(
            self.variable['propertyLength'])

        self.variable['properties'] = {}
        self.variable['properties']['userProperty'] = {}
        self.variable_size = 2 + self.variable['propertyLength']
        properties = properties[required:]

        i = 0
        while i < self.variable['propertyLength']:
            if properties[i] == 0x0B:
                if 'subscription_identifier' not in self.variable['properties'].keys():
                    self.variable['properties']['subscription_identifier'] = struct.unpack(
                        "!B", properties[i+1: i+2])[0]
                else:
                    raise MQTTError(
                        "Malformed Packet: Subscription Identifier already exist")
            if properties[i] == 0x26:
                offset1, str1 = readCustomUTF8String(properties[i+1:])
                offset2, str2 = readCustomUTF8String(properties[i+1+offset1:])
                if str1 not in self.variable['properties']['userProperty'].keys():
                    self.variable['properties']['userProperty'][str1] = [str2]
                else:
                    self.variable['properties']['userProperty'][str1].append(str2)
                i += offset1+offset2
            i = i + 1

    def parsePayloadHeader(self):
        offset = self.fixed_size + self.variable_size + 1
        self.payload_size = self.fixed['remainingLength'] - self.variable_size
        payloadHeader = self.data[offset:]

        self.payload['unsubscriptions'] = []
        while(len(payloadHeader) != 0):
            offset, topic = readCustomUTF8String(payloadHeader)
            payloadHeader = payloadHeader[offset:]
            self.payload['unsubscriptions'].append(topic)
        
    def parse(self):
        self.parseFixedHeader()
        self.parseVariableHeader()
        self.parsePayloadHeader()

if __name__ == "__main__":
    # 1. fixed header
    fixed = b"\xa0"

    # 2. variable header
    packet_id = b"\x00\x10"
    userProperty = b"\x26" + CustomUTF8.encode("Friday") + CustomUTF8.encode("Monday")

    # 2.1. properties
    properties = userProperty
    property_length = VariableByte.encode(len(properties))

    variableHeader = packet_id  + property_length + properties
    length_of_variable_header = len(variableHeader)

    
    # 3. payload
    topic1 = CustomUTF8.encode("topic")
    topic2 =  CustomUTF8.encode("a/b")
    payload = topic1+topic2

    remainingLength = VariableByte.encode(length_of_variable_header+len(payload))


    data = fixed + remainingLength + variableHeader + payload
    data = struct.pack("!{}s".format(len(data)), data)

    packet = UnsubscribePacket(data)
    packet.parseFixedHeader()
    packet.parseVariableHeader()
    packet.parsePayloadHeader()
    print(packet.fixed)
    print(packet.variable)
    print(packet.payload)
