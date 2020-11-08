#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import VariableByte, MQTTError, CustomUTF8, BinaryData

class ConnectPacket(MQTTPacket):
	def __init__(self, data : bytes):
		self.data=data
		self.fixed={}
		self.variable={}
		self.payload={}
			

	def parseVariableHeader(self) -> None:
		offset = len(VariableByte.encode(self.fixed['remainingLength']))+1
		variableHeader = self.data[offset:10+offset]
		protocol_name_bytes = struct.unpack(">6s", variableHeader[:6])
		length_msb, length_lsb, name = struct.unpack(">2b4s", variableHeader[:6])
		self.variable['length']=(length_msb<<8)+length_lsb
		self.variable['name']=name.decode("utf-8")
		variableHeader = variableHeader[6:]
		protocol_version = struct.unpack(">B", variableHeader[:1])[0]
		self.variable['protocolVersion']=protocol_version
		variableHeader=variableHeader[1:]
		connectFlags = struct.unpack(">B", variableHeader[:1])[0]
		self.variable['usernameFlag'] = (connectFlags & 128 == 128)
		self.variable['passwordFlag'] = (connectFlags & 64 == 64)
		self.variable['willRetain'] = (connectFlags & 32 == 32)
		self.variable['willQoS'] = connectFlags & 24 #16+8
		self.variable['willFlag'] = (connectFlags & 4 == 4)
		self.variable['cleanStart'] = (connectFlags & 2 == 2)
		self.variable['reserved'] = (connectFlags & 1 == 1)
		variableHeader=variableHeader[1:]
		keep_alive_msb, keep_alive_lsb = struct.unpack(">2B", variableHeader[:2])
		keep_alive = (keep_alive_msb<<8)+keep_alive_lsb
		self.variable['KeepAlive']=keep_alive
		

	def parsePayloadHeader(self) -> bool:
		offset = len(VariableByte.encode(self.fixed['remainingLength']))+1
		payloadHeader=self.data[10+offset:]
		num=b""
		for byte in payloadHeader:
			num+=struct.pack("<B", byte)
			if byte<0x80:
				break
		required=len(num)
		self.payload['length'] = struct.unpack(">{}s".format(required), num)[0]
		self.payload['length'] = VariableByte.decode(self.payload['length'])
		self.payload['properties']={}
		self.payload['properties']['topicAliasMaximum']=0
		self.payload['properties']['requestResponseInformation']=1
		self.payload['properties']['userProperty']={}
		payloadHeader=payloadHeader[required:]
		i=0
		while i<len(payloadHeader):
			if payloadHeader[i]==0x11:
				if 'sessionExpiry' not in self.payload['properties'].keys():
					self.payload['properties']['sessionExpiry']=struct.unpack(">I", payloadHeader[i+1:i+5])[0]
					i+=3
				else:
					raise MQTTError("Malformed Packet : sessionExpiry already exists")
			if payloadHeader[i]==0x21:
				if 'receiveMaximum' not in self.payload['properties'].keys():
					self.payload['properties']['receiveMaximum']=struct.unpack(">H", payloadHeader[i+1:i+3])[0]
					if self.payload['properties']['receiveMaximum']==0:
						raise MQTTError("Malformed Packet : sessionExpiry is set to 0")
					i+=1
				else:
					raise MQTTError("Malformed Packet : receiveMaximum already exists")
			if payloadHeader[i]==0x27:
				if 'maximumPacketSize' not in self.payload['properties'].keys():
					self.payload['properties']['maximumPacketSize']=struct.unpack(">I", payloadHeader[i+1:i+5])[0]
					if self.payload['properties']['maximumPacketSize']==0:
						raise MQTTError("Malformed Packet : sessionExpiry is set to 0")
					i+=3
				else:
					raise MQTTError("Malformed Packet : sessionExpiry already exists")
			if payloadHeader[i]==0x22:
				self.payload['properties']['topicAliasMaximum']=struct.unpack(">H", payloadHeader[i+1:i+3])[0]
				i+=1
			if payloadHeader[i]==0x19:
				self.payload['properties']['requestResponseInformation']=struct.unpack(">B", payloadHeader[i+1:i+2])[0]
				if self.payload['properties']['requestResponseInformation'] not in [0, 1]:
					raise MQTTError("Malformed Packet : requestResponseInformation is not 0 or 1")
			if payloadHeader[i]==0x26:
				OFFSET_TO_READ_1_START=i+1
				OFFSET_TO_READ_1_END=i+3
				to_read = payloadHeader[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END]
				str1size = struct.unpack(">H", to_read)[0]
				str1 = struct.unpack(">{}s".format(str1size+OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START), payloadHeader[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END+str1size])[0]
				OFFSET_TO_READ_2_START=i+3+str1size
				OFFSET_TO_READ_2_END=i+5+str1size
				to_read2 = payloadHeader[OFFSET_TO_READ_2_START:OFFSET_TO_READ_2_END]
				str2size = struct.unpack(">H", to_read2)[0]
				str2 = struct.unpack(">{}s".format(str2size+OFFSET_TO_READ_2_END-OFFSET_TO_READ_2_START), payloadHeader[OFFSET_TO_READ_2_START:OFFSET_TO_READ_2_END+str2size])[0]
				if CustomUTF8.decode(str1) not in self.payload['properties']['userProperty'].keys():
					self.payload['properties']['userProperty'][CustomUTF8.decode(str1)]=[CustomUTF8.decode(str2)]
				else:
					self.payload['properties']['userProperty'][CustomUTF8.decode(str1)].append(CustomUTF8.decode(str2))
				i+=OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START+OFFSET_TO_READ_2_END-OFFSET_TO_READ_2_START+3
			if payloadHeader[i]==0x15:
				if 'authMethod' not in self.payload['properties'].keys():
					OFFSET_TO_READ_1_START=i+1
					OFFSET_TO_READ_1_END=i+3
					to_read = payloadHeader[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END]
					str1size = struct.unpack(">H", to_read)[0]
					self.payload['properties']['authMethod'] = CustomUTF8.decode(struct.unpack(">{}s".format(str1size+OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START), payloadHeader[OFFSET_TO_READ_1_START:OFFSET_TO_READ_1_END+str1size])[0])
					i+=OFFSET_TO_READ_1_END-OFFSET_TO_READ_1_START+str1size-1
				else:
					raise MQTTError("Malformed Packet : authMethod already exists")
			if payloadHeader[i]==0x16:
				if 'authData' not in self.payload['properties'].keys():
					OFFSET_TO_READ_START=i+1
					OFFSET_TO_READ_END=i+3
					to_read = payloadHeader[OFFSET_TO_READ_START:OFFSET_TO_READ_END]
					datasize = struct.unpack(">H", to_read)[0]
					self.payload['properties']['authData'] = payloadHeader[OFFSET_TO_READ_END:OFFSET_TO_READ_END+datasize]
					i+=OFFSET_TO_READ_END-OFFSET_TO_READ_START+datasize-1
			i=i+1
		return True

if __name__=="__main__":
	byte_data = b"\x10\x0f\x00\x04MQTT\x05\xfe\x01\xff\x80\x01\x11\x00\x00\x00\x02\x21\x00\x02\x26"+CustomUTF8.encode("salut")+CustomUTF8.encode("Emil")+b"\x26"+CustomUTF8.encode("salut")+CustomUTF8.encode("bunaziua")+b"\x26"+CustomUTF8.encode("hello")+CustomUTF8.encode("Nicky")+b"\x15"+CustomUTF8.encode("userpass")+b"\x16\x00\x04\x02\x03\x04\x05"+b"\x26"+CustomUTF8.encode("salut")+CustomUTF8.encode("Andrei")
	data = struct.pack(">{}s".format(len(byte_data)), byte_data)
	packet = ConnectPacket(data)
	packet.parseFixedHeader()
	packet.parseVariableHeader()
	packet.parsePayloadHeader()
	print(packet.fixed)
	print(packet.variable)
	print(packet.payload)