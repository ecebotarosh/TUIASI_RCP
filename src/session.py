#!/usr/bin/env python3

import struct
from MQTTPacket import MQTTPacket
from ConnectPacket import ConnectPacket

class Session:
	def __init__(self, data):
		self.data=data

	def classifyData(self) -> MQTTPacket:
		fixed_part = self.data[:2]
		byte1, byte2 = struct.unpack(">2B", fixed_part)
		if byte1 // 16==1:
			if byte1 % 16 !=0:
				print("Returning MalformedPacket")
				return MQTTPacket(data)
			else:
				print("Returning ConnectPacket")
				return ConnectPacket(data)
		
			


if __name__=="__main__":
	byte_data = b"\x10\x0f\x15\x30"
	data = struct.pack(">{}s".format(len(byte_data)), byte_data)
	session = Session(data)
	packet = session.classifyData()
	packet.parseFixedHeader()
