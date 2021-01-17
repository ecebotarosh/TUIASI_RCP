#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import VariableByte, MQTTError, CustomUTF8, BinaryData, readCustomUTF8String


class SubscribePacket(MQTTPacket):
    def __init__(self, data):
        self.data = data
        self.fixed = {}
        self.fixed_size = 0
        self.variable = {}
        self.variable_size = 0
        self.payload = {}
        self.payload_size = 0

    def parseFixedHeader(self):
        fixed_part = self.data[:1]
	num=b""
	for byte in self.data[1:]:
	    num+=struct.pack("!B", byte)
		if byte<0x80:
		    break
	required=len(num)
	self.fixed['type'], self.fixed['remainingLength'] = struct.unpack("!B{}s".format(required), fixed_part+num)
        if self.fixed['type'] & 0x0F != 0x02:
            raise MQTTError("Malformed Packet")
	self.fixed['type']>>=4
	self.fixed['remainingLength']=VariableByte.decode(self.fixed['remainingLength'])
	self.fixed_size=1+required
 

    def parseVariableHeader(self):
        variableHeader = self.data[self.fixed_size:]

        # subscribe packed id
        packet_id_MSB, packet_id_LSB = struct.unpack("!2b", variableHeader[:2])
        self.variable['packet_id'] = (packet_id_MSB << 8) + packet_id_LSB
        variableHeader = variableHeader[2:]

        # 2 bytes so far

        properties = self.data[self.fixed_size + 2:]
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

        self.payload['subscriptions'] = []
        subscriptionList = []
        while(len(payloadHeader) != 0):
            offset, topic = readCustomUTF8String(payloadHeader)
            payloadHeader = payloadHeader[offset:]
            # subscribeOptions
            subscriptionOptions = struct.unpack("!B", payloadHeader[:1])[0]
            reserved = subscriptionOptions & 192
            if reserved:
                raise MQTTError("Malformed Packet")
            retainHandling = subscriptionOptions & 48
            RAP = subscriptionOptions & 8
            NL = subscriptionOptions & 4
            QoS = subscriptionOptions & 3
            subscriptionList.append({topic:{'retainHandling': retainHandling, 'RAP': RAP, 'NL': NL, 'QoS': QoS}})
            self.payload['subscriptions'].append(subscriptionList)
            payloadHeader = payloadHeader[1:]
            #self.payload['subscriptions'] este o lista de liste de 2 elemente : str si dict

        def parse(self) -> None:
            self.parseFixedHeader()
            self.parseVariableHeader()
            self.parsePayloadHeader()


if __name__ == "__main__":
    # 1. fixed header
    fixed = b"\x82"

    # 2. variable header
    packet_id = b"\x00\x10"
    userProperty = b"\x26" + CustomUTF8.encode("Friday") + CustomUTF8.encode("Monday")

    # 2.1. properties
    properties = userProperty
    property_length = VariableByte.encode(len(properties))

    variableHeader = packet_id  + property_length + properties
    length_of_variable_header = len(variableHeader)

    
    # 3. payload
    topic = CustomUTF8.encode("topic")
    optiuni = b"\x0d"

    payload = topic + optiuni

    remainingLength = VariableByte.encode(length_of_variable_header+len(payload))


    data = fixed + remainingLength + variableHeader + payload
    data = struct.pack("!{}s".format(len(data)), data)

    packet = SubscribePacket(data)
    packet.parseFixedHeader()
    packet.parseVariableHeader()
    packet.parsePayloadHeader()
    print(packet.fixed)
    print(packet.variable)
    print(packet.payload)
