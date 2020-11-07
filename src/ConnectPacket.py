#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket


class ConnectPacket(MQTTPacket):
	def __init__(self, data):
		self.data=data
		self.fixed={}
		self.variable={}
		self.payload={}
			

	def parseVariableHeader(self):
		variableHeader = self.data[2:12]
		protocol_name_bytes = struct.unpack(">6s", variableHeader[:6])
		length_msb, length_lsb, name = struct.unpack(">2b4s", variableHeader[:6])
		self.variable['length']=length_msb*0xff+length_lsb
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
		keep_alive = keep_alive_msb*0xff+keep_alive_lsb
		self.variable['KeepAlive']=keep_alive
		

	def parsePayloadHeader(self):
		pass		

if __name__=="__main__":
	byte_data = b"\x10\x0f\x00\x04MQTT\x05\xfe\x00\xff"
	data = struct.pack(">{}s".format(len(byte_data)), byte_data)
	packet = ConnectPacket(data)
	packet.parseFixedHeader()
	packet.parseVariableHeader()
	print(packet.fixed)
	print(packet.variable)