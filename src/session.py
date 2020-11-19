#!/usr/bin/env python3

import struct
from MQTTPacket import MQTTPacket
from ConnectPacket import ConnectPacket
from ConnackPacket import ConnackPacket
from aux import MQTTError

class Session:
	def __init__(self):
		self.data=b""

	def registerNewData(self, data:bytes):
		self.data=data

	def classifyData(self) -> MQTTPacket:
		fixed_part = self.data[:2]
		byte1, byte2 = struct.unpack("!2B", fixed_part)
		if byte1 // 16==1:
			if byte1 % 16 !=0:
				raise MQTTError("Malformed Packet")
			else:
				print("Returning ConnectPacket")
				return ConnectPacket(self.data)

	def handleConnection(self, packet:MQTTPacket) -> MQTTPacket:
		if isinstance(packet, ConnectPacket):
			packet.parseFixedHeader()
			packet.parseVariableHeader()
			packet.parsePayloadHeader()
			print(packet.fixed)
			print(packet.variable)
			print(packet.payload)
			return ConnackPacket(ConnackPacket.generatePacketData(False, 0, {'SessionExpiryInterval':30}))

		
			


if __name__=="__main__":
	byte_data = b"\x10\x0f\x15\x30"
	data = struct.pack(">{}s".format(len(byte_data)), byte_data)
	session = Session(data)
	packet = session.classifyData()
	packet.parseFixedHeader()
