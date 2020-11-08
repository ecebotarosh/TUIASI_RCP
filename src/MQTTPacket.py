#!/usr/bin/env python3

import struct
from aux import VariableByte

class MQTTPacket:
	def __init__(self, data):
		self.data=data
		self.fixed=b""
		self.variable=b""
		self.payload=b""

	def parseFixedHeader(self):
		fixed_part = self.data[:1]
		num=b""
		for byte in self.data[1:]:
			num+=struct.pack("<B", byte)
			if byte<0x80:
				break
		required=len(num)
		self.fixed['type'], self.fixed['remainingLength'] = struct.unpack(">B{}s".format(required), fixed_part+num)
		self.fixed['remainingLength']=VariableByte.decode(self.fixed['remainingLength'])
		
	def parseVariableHeader(self):
		pass

	def parsePayloadHeader(self):
		pass		