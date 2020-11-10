#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import VariableByte, MQTTError, CustomUTF8, BinaryData


class ConnectPacket(MQTTPacket):
    def __init__(self, data: bytes):
        self.data = data
        self.fixed = {}
        self.fixed_size = 0
        self.variable = {}
        self.variable_size = 0
        self.payload = {}
        self.payload_size = 0

    def parseVariableHeader(self) -> None:
        variableHeader = self.data[self.fixed_size:]
        protocol_name_bytes = struct.unpack("!6s", variableHeader[:6])
        length_msb, length_lsb, name = struct.unpack(
            "!2b4s", variableHeader[:6])
        self.variable['length'] = (length_msb << 8)+length_lsb
        self.variable['name'] = name.decode("utf-8")
        variableHeader = variableHeader[6:]
        protocol_version = struct.unpack("!B", variableHeader[:1])[0]
        self.variable['protocolVersion'] = protocol_version
        variableHeader = variableHeader[1:]
        connectFlags = struct.unpack("!B", variableHeader[:1])[0]
        self.variable['usernameFlag'] = (connectFlags & 128 == 128)
        self.variable['passwordFlag'] = (connectFlags & 64 == 64)
        self.variable['willRetain'] = (connectFlags & 32 == 32)
        self.variable['willQoS'] = connectFlags & 24  # 16+8
        self.variable['willFlag'] = (connectFlags & 4 == 4)
        self.variable['cleanStart'] = (connectFlags & 2 == 2)
        self.variable['reserved'] = (connectFlags & 1 == 1)
        variableHeader = variableHeader[1:]
        keep_alive_msb, keep_alive_lsb = struct.unpack(
            "!2B", variableHeader[:2])
        keep_alive = (keep_alive_msb << 8)+keep_alive_lsb
        self.variable['KeepAlive'] = keep_alive
        # 10 bytes is the common variable header, without properties
        properties = self.data[10+self.fixed_size:]
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

        self.variable['properties']['requestResponseInformation'] = 1
        self.variable['properties']['userProperty'] = {}

        self.variable_size = self.variable['propertyLength']+10
        properties = properties[required:]
        i = 0
        while i < self.variable['propertyLength']:
            if properties[i] == 0x11:
                if 'sessionExpiry' not in self.variable['properties'].keys():
                    self.variable['properties']['sessionExpiry'] = struct.unpack(
                        "!I", properties[i+1:i+5])[0]
                    i += 4
                else:
                    raise MQTTError(
                        "Malformed Packet : sessionExpiry already exists")
            if properties[i] == 0x21:
                if 'receiveMaximum' not in self.variable['properties'].keys():
                    self.variable['properties']['receiveMaximum'] = struct.unpack(
                        "!H", properties[i+1:i+3])[0]
                    if self.variable['properties']['receiveMaximum'] == 0:
                        raise MQTTError(
                            "Malformed Packet : sessionExpiry is set to 0")
                    i += 2
                else:
                    raise MQTTError(
                        "Malformed Packet : receiveMaximum already exists")
            if properties[i] == 0x27:
                if 'maximumPacketSize' not in self.variable['properties'].keys():
                    self.variable['properties']['maximumPacketSize'] = struct.unpack(
                        "!I", properties[i+1:i+5])[0]
                    if self.variable['properties']['maximumPacketSize'] == 0:
                        raise MQTTError(
                            "Malformed Packet : sessionExpiry is set to 0")
                    i += 4
                else:
                    raise MQTTError(
                        "Malformed Packet : sessionExpiry already exists")
            if properties[i] == 0x22:
                if 'topicAliasMaximum' not in self.variable['properties'].keys():
                    self.variable['properties']['topicAliasMaximum'] = struct.unpack(
                        "!H", properties[i+1:i+3])[0]
                else:
                    raise MQTTError(
                        "Malformed Packet : topicAliasMaximum already exists")
                i += 2
            if properties[i] == 0x19:
                if 'requestResponseInformation' not in self.variable['properties'].keys():
                    self.variable['properties']['requestResponseInformation'] = struct.unpack(
                        "!B", properties[i+1:i+2])[0]
                    if self.variable['properties']['requestResponseInformation'] not in [0, 1]:
                        raise MQTTError(
                        "Malformed Packet : requestResponseInformation is not 0 or 1")
                else:
                    raise MQTTError(
                        "Malformed Packet : requestResponseInformation already exists")
            if properties[i] == 0x17:
                if 'requestProblemInformation' not in self.variable['properties'].keys():
                    self.variable['properties']['requestProblemInformation'] = struct.unpack(
                        "!B", properties[i+1:i+2])[0]
                    if self.variable['properties']['requestProblemInformation'] not in [0, 1]:
                        raise MQTTError(
                            "Malformed Packet : requestProblemInformation is not in 0 or 1")
                else:
                    raise MQTTError(
                        "Malformed Packet : requestProblemInformation already exists")

            if properties[i] == 0x26:
                OFFSET_TO_READ_1_START = i+1
                OFFSET_TO_READ_1_END = i+3
                to_read = properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END]
                str1size = struct.unpack("!H", to_read)[0]
                str1 = struct.unpack("!{}s".format(str1size+OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START),
                                     properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END+str1size])[0]
                OFFSET_TO_READ_2_START = i+3+str1size
                OFFSET_TO_READ_2_END = i+5+str1size
                to_read2 = properties[OFFSET_TO_READ_2_START:OFFSET_TO_READ_2_END]
                str2size = struct.unpack("!H", to_read2)[0]
                str2 = struct.unpack("!{}s".format(str2size+OFFSET_TO_READ_2_END-OFFSET_TO_READ_2_START),
                                     properties[OFFSET_TO_READ_2_START:OFFSET_TO_READ_2_END+str2size])[0]
                if CustomUTF8.decode(str1) not in self.variable['properties']['userProperty'].keys():
                    self.variable['properties']['userProperty'][CustomUTF8.decode(str1)] = [
                        CustomUTF8.decode(str2)]
                else:
                    self.variable['properties']['userProperty'][CustomUTF8.decode(
                        str1)].append(CustomUTF8.decode(str2))
                i += 4+len(CustomUTF8.decode(str1))+len(CustomUTF8.decode(str2))
            if properties[i] == 0x15:
                if 'authMethod' not in self.variable['properties'].keys():
                    OFFSET_TO_READ_1_START = i+1
                    OFFSET_TO_READ_1_END = i+3
                    to_read = properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END]
                    str1size = struct.unpack("!H", to_read)[0]
                    self.variable['properties']['authMethod'] = CustomUTF8.decode(struct.unpack("!{}s".format(
                        str1size+OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START), properties[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END+str1size])[0])
                    i += OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START+str1size
                else:
                    raise MQTTError(
                        "Malformed Packet : authMethod already exists")
            if properties[i] == 0x16:
                if 'authData' not in self.variable['properties'].keys():
                    OFFSET_TO_READ_START = i+1
                    OFFSET_TO_READ_END = i+3
                    to_read = properties[OFFSET_TO_READ_START:OFFSET_TO_READ_END]
                    datasize = struct.unpack("!H", to_read)[0]
                    self.variable['properties']['authData'] = properties[OFFSET_TO_READ_END:OFFSET_TO_READ_END+datasize]
                    i += OFFSET_TO_READ_END-OFFSET_TO_READ_START+datasize
                else:
                    raise MQTTError(
                        "Malformed Packet : authentication data already exists")
            i = i+1

        if 'sessionExpiry' not in self.variable['properties'].keys():
            self.variable['properties']['sessionExpiry'] = 0
        if 'receiveMaximum' not in self.variable['properties'].keys():
            self.variable['properties']['receiveMaximum'] = 65535
        if 'topicAliasMaximum' not in self.variable['properties'].keys():
            self.variable['properties']['topicAliasMaximum'] = 0
        if 'requestResponseInformation' not in self.variable['properties'].keys():
            self.variable['properties']['requestResponseInformation'] = 0
        if 'requestProblemInformation' not in self.variable['properties'].keys():
            self.variable['properties']['requestProblemInformation'] = 1

    def parsePayloadHeader(self):
        offset = self.fixed_size+self.variable_size+1
        self.payload_size = self.fixed['remainingLength']-self.variable_size
        payloadHeader = self.data[offset:]
        required = struct.unpack("!H", payloadHeader[:2])[0]
        self.payload['clientID'] = struct.unpack(
            "!{}s".format(required+2), payloadHeader[:required+2])[0]
        self.payload['clientID'] = CustomUTF8.decode(self.payload['clientID'])
        payloadHeader = payloadHeader[required+2:]
        if self.variable['willFlag']:
            self.payload['willProperties'] = {}
            self.payload['willProperties']['userProperty'] = {}
            num = b""
            for byte in payloadHeader:
                num += struct.pack("!B", byte)
                if byte < 0x80:
                    break
            self.payload['willProperties']['willLength'] = VariableByte.decode(
                num)
            i = 0
            payloadHeader = payloadHeader[len(num):]
            while i < self.payload['willProperties']['willLength']:
                if payloadHeader[i] == 0x18:
                    if 'willDelayInterval' not in self.payload['willProperties'].keys():
                        self.payload['willProperties']['willDelayInterval'] = struct.unpack(
                            "!I", payloadHeader[i+1:i+5])[0]
                    else:
                        raise MQTTError(
                            "Malformed Packet : willDelay already exists")
                    i += 4
                if payloadHeader[i] == 0x01:
                    if 'payloadFormatIndicator' not in self.payload['willProperties'].keys():
                        self.payload['willProperties']['payloadFormatIndicator'] = struct.unpack(
                            "!B", payloadHeader[i+1:i+2])[0]
                    else:
                        raise MQTTError(
                            "Malformed Packet : payloadFormatIndicator already exists")
                    i += 1
                if payloadHeader[i] == 0x02:
                    if 'messageExpiryInterval' not in self.payload['willProperties'].keys():
                        self.payload['willProperties']['messageExpiryInterval'] = (
                            True, struct.unpack("!I", payloadHeader[i+1:i+5])[0])
                    else:
                        raise MQTTError(
                            "Malformed Packet : messageExpiryInterval already exists")
                    i += 4
                    
                if payloadHeader[i] == 0x03:
                    if 'contentType' not in self.payload['willProperties'].keys():
                        strlen = struct.unpack("!H", payloadHeader[i+1:i+3])[0]
                        self.payload['willProperties']['contentType'] = struct.unpack(
                            "!{}s".format(strlen), payloadHeader[i+3:i+strlen+3])[0].decode('utf-8')
                    else:
                        raise MQTTError(
                            "Malformed Packet : contentType already exists")
                    i += 2+strlen

                if payloadHeader[i] == 0x08:
                    if 'responseTopic' not in self.payload['willProperties'].keys():
                        strlen = struct.unpack("!H", payloadHeader[i+1:i+3])[0]
                        self.payload['willProperties']['responseTopic'] = struct.unpack(
                            "!{}s".format(strlen), payloadHeader[i+3:i+strlen+3])[0].decode('utf-8')
                    else:
                        raise MQTTError(
                            "Malformed Packet : responseTopic already exists")
                    i += 2+strlen
                if payloadHeader[i] == 0x09:
                    if 'correlationData' not in self.payload['willProperties'].keys():
                        length = struct.unpack("!H", payloadHeader[i+1:i+3])[0]
                        self.payload['willProperties']['correlationData'] = payloadHeader[i+1:i+3+length]
                    else:
                        raise MQTTError("Malformed Packet : correlationData already exists")
                    i += 2+length
                if payloadHeader[i] == 0x26:
                    OFFSET_TO_READ_1_START = i+1
                    OFFSET_TO_READ_1_END = i+3
                    to_read = payloadHeader[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END]
                    str1size = struct.unpack("!H", to_read)[0]
                    str1 = struct.unpack("!{}s".format(str1size+OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START), payloadHeader[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END+str1size])[0]
                    OFFSET_TO_READ_2_START = i+3+str1size
                    OFFSET_TO_READ_2_END = i+5+str1size
                    to_read2 = payloadHeader[OFFSET_TO_READ_2_START:OFFSET_TO_READ_2_END]
                    str2size = struct.unpack("!H", to_read2)[0]
                    str2 = struct.unpack("!{}s".format(str2size+OFFSET_TO_READ_2_END-OFFSET_TO_READ_2_START), payloadHeader[OFFSET_TO_READ_2_START:OFFSET_TO_READ_2_END+str2size])[0]
                    if CustomUTF8.decode(str1) not in self.payload['willProperties']['userProperty'].keys():
                        self.payload['willProperties']['userProperty'][CustomUTF8.decode(str1)] = [CustomUTF8.decode(str2)]
                    else:
                        self.payload['willProperties']['userProperty'][CustomUTF8.decode(
                            str1)].append(CustomUTF8.decode(str2))
                    i += 4+len(CustomUTF8.decode(str1))+len(CustomUTF8.decode(str2))
                i += 1

            #TODO : Check unusual offsets
            offset = self.payload['willProperties']['willLength']
            strlen = struct.unpack("!H", payloadHeader[offset:offset+2])[0]
            self.payload['willTopic']=CustomUTF8.decode(struct.unpack("!{}s".format(2+strlen), payloadHeader[offset:offset+2+strlen])[0])

            if 'willDelayInterval' not in self.payload['willProperties'].keys():
                self.payload['willProperties']['willDelayInterval'] = 0
            if 'payloadFormatIndicator' not in self.payload['willProperties'].keys():
                self.payload['willProperties']['payloadFormatIndicator'] = 0
            if 'messageExpiryInterval' not in self.payload['willProperties'].keys():
                self.payload['willProperties']['messageExpiryInterval'] = (
                    False, 0)



if __name__ == "__main__":

    clientID = CustomUTF8.encode("r3allyrandomid")

    willDelay = struct.pack("!I", 35)
    payloadFormatIndicator = b"\x01\x01"
    messageExpiryInterval = b"\x02"+struct.pack("!I", 32)
    willTopic = CustomUTF8.encode("pc/temp")
    correlationData = b"\x09"+b"\x00\x02\x04\x08"
    contentType = b"\x03"+CustomUTF8.encode("application/x-pdf")
    responseTopic = b"\x08"+CustomUTF8.encode("my response topic")
    userProperties = b"\x26"+CustomUTF8.encode("salut_din_will")+CustomUTF8.encode("dev")
    will = b"\x18"+willDelay+ payloadFormatIndicator + messageExpiryInterval+userProperties+contentType+ correlationData 
    willLength = VariableByte.encode(len(will))
    otherProps = willTopic
    variableContents = b"\x00\x04MQTT\x05\xfe\x01\xff"
    properties = b"\x11\x00\x00\x00\x02\x21\x00\x02\x26"+CustomUTF8.encode("salut")+CustomUTF8.encode("Emil")+b"\x26"+CustomUTF8.encode("salut")+CustomUTF8.encode("bunaziua")+b"\x26"+CustomUTF8.encode(
        "hello")+CustomUTF8.encode("Nicky")+b"\x15"+CustomUTF8.encode("userpass")+b"\x16\x00\x04\x02\x03\x04\x05"+b"\x26"+CustomUTF8.encode("salut")+CustomUTF8.encode("Andrei")
    propertyLength = VariableByte.encode(len(properties))
    byte_data = b"\x10"+VariableByte.encode(
        len(variableContents+propertyLength+properties+clientID+willLength+will+willTopic))

    packetContents = byte_data+variableContents + \
        propertyLength+properties+clientID+willLength+will + willTopic
    data = struct.pack("!{}s".format(len(packetContents)), packetContents)
    packet = ConnectPacket(data)
    packet.parseFixedHeader()
    packet.parseVariableHeader()
    packet.parsePayloadHeader()
    print(packet.fixed)
    print(packet.variable)
    print(packet.payload)
