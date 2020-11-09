#!/usr/bin/env python3

import struct
from aux import VariableByte

class MQTTPacket:
	def __init__(self, data):
		self.data=data
		self.fixed={}
		self.fixed_size=0
		self.variable={}
		self.variable_size=0
		self.payload={}
		self.payload_size=0


	def parseFixedHeader(self):
		fixed_part = self.data[:1]
		num=b""
		for byte in self.data[1:]:
			num+=struct.pack("<B", byte)
			if byte<0x80:
				break
		required=len(num)
		self.fixed['type'], self.fixed['remainingLength'] = struct.unpack(">B{}s".format(required), fixed_part+num)
		self.fixed['type']>>=4
		self.fixed['remainingLength']=VariableByte.decode(self.fixed['remainingLength'])
		self.fixed_size=1+required
		
	def parseVariableHeader(self):
		pass

	def parsePayloadHeader(self):
		pass		


