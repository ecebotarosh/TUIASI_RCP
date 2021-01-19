#!/usr/bin/env python3

from MQTTPacket import MQTTPacket
import struct
from aux import CustomUTF8, VariableByte, BinaryData


class ConnackPacket(MQTTPacket):
    def __init__(self, data):
        self.data = data
        self.fixed = {}
        self.fixed_size = 0
        self.variable = {}
        self.variable_size = 0
        self.payload = {}
        self.payload_size = 0

    @staticmethod
    def generatePacketData(ack_flags: bool, reason_code: int, properties: dict) -> bytes:
        data = b"\x20"
        if ack_flags:
            flags = b"\x01"
        else:
            flags = b"\x00"
        rc = struct.pack("!B", reason_code)
        props = b""
        myProperties = list(properties.keys())

        if 'SessionExpiryInterval' in myProperties:
            props += b"\x11" + \
                struct.pack("!I", properties['SessionExpiryInterval'])
            myProperties.remove('SessionExpiryInterval')
        if 'ReceiveMaximum' in myProperties:
            props += b"\x21"+struct.pack("!H", properties['ReceiveMaximum'])
            myProperties.remove('ReceiveMaximum')
        if 'MaximumQoS' in myProperties:
            props += b"\x24"+struct.pack("!B", properties['MaximumQoS'])
            myProperties.remove('MaximumQoS')
        if 'RetainAvailable' in myProperties:
            props += b"\x25"+struct.pack("!B", properties['RetainAvailable'])
            myProperties.remove('RetainAvailable')
        if 'MaximumPacketSize' in myProperties:
            props += b"\x27"+struct.pack("!I". properties['MaximumPacketSize'])
            myProperties.remove('MaximumPacketSize')
        if 'AssignedClientId' in myProperties:
            props += b"\x12"+CustomUTF8.encode(properties['AssignedClientId'])
            myProperties.remove('AssignedClientId')
        if 'TopicAliasMaximum' in myProperties:
            props += b"\x22"+struct.pack("!H". properties['TopicAliasMaximum'])
            myProperties.remove('TopicAliasMaximum')
        if 'ReasonString' in myProperties:
            props += b"\x1F"+CustomUTF8.encode(properties['ReasonString'])
            myProperties.remove('ReasonString')
        if 'UserProperty' in myProperties:
            for key in properties['UserProperty'].keys():
                for value in properties['UserProperty'][key]:
                    props += b"\x26" + \
                        CustomUTF8.encode(key)+CustomUTF8.encode(value)
            myProperties.remove('UserProperty')
        if 'WildcardSubscriptionAvailable' in myProperties:
            props += b"\x28" + \
                struct.pack("!B", properties['WildcardSubscriptionAvailable'])
            myProperties.remove('WildcardSubscriptionAvailable')
        if 'SubscriptionIdentifiersAvailable' in myProperties:
            props += b"\x29" + \
                struct.pack(
                    "!B", properties['SubscriptionIdentifiersAvailable'])
            myProperties.remove('SubscriptionIdentifiersAvailable')
        if 'SharedSubscriptionAvailable' in myProperties:
            props += b"\x2A" + \
                struct.pack("!B", properties['SharedSubscriptionAvailable'])
            myProperties.remove('SharedSubscriptionAvailable')
        if 'ServerKeepAlive' in myProperties:
            props += b"\x13"+struct.pack("!H", properties['ServerKeepAlive'])
            myProperties.remove('ServerKeepAlive')
        if 'ResponseInformation' in myProperties:
            props += b"\x1A" + \
                CustomUTF8.encode(properties['ResponseInformation'])
            myProperties.remove('ResponseInformation')
        if 'ServerReference' in myProperties:
            props += b"\x1C"+CustomUTF8.encode(properties['ServerReference'])
            myProperties.remove('ServerReference')
        if 'AuthenticationMethod' in myProperties:
            props += b"\x15" + \
                CustomUTF8.encode(properties['AuthenticationMethod'])
            myProperties.remove('AuthenticationMethod')
        if 'AuthenticationData' in myProperties:
            props += b"\x16" + \
                BinaryData.fromBytesToBinary(properties['AuthenticationData'])
            myProperties.remove('AuthenticationData')

        if myProperties != []:
            raise ValueError("Unknown property was not parsed")
        propertyLength = VariableByte.encode(len(props))
        # 1 pentru flags si 1 pentru rc
        remainingLength = VariableByte.encode(2+len(propertyLength)+len(props))
        # len(propertyLength) pare stupid, dar e necesar
        # propertyLength e format ca variable Byte si face parte din continutul pachetului.
        data += remainingLength + flags + rc + propertyLength + props
        return data
