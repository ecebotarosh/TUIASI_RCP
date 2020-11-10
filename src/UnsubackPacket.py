#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import VariableByte

class UnsubackPacket(MQTTPacket):
	def parseVariableHeader(self)->None:
		offset=len(VariableByte.encode(self.fixed['remainingLength']))+1
		variableHeader=self.data[self.fixed_size:]
		length_msb,length_lsb=struct.unpack("!2B",variableHeader[:2])
		self.variable['length']=(length_msb<<8)+length_lsb

if __name__=="__main__":
	byte_data = b"\x10\x0f\x01\x00"
	data = struct.pack(">{}s".format(len(byte_data)), byte_data)
	packet=UnsubackPacket(data)
	packet.parseFixedHeader()
	packet.parseVariableHeader()
	print(packet.fixed)
	print(packet.variable)