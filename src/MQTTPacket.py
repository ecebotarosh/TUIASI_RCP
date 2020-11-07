#!/usr/bin/env python3

import struct

class MQTTPacket:
	def __init__(self, data):
		self.data=data
		self.fixed=b""
		self.variable=b""
		self.payload=b""

	def parseFixedHeader(self):
		fixed_part = self.data[:2]
		self.fixed['type'], self.fixed['remainingLength'] = struct.unpack(">2B", fixed_part)

	def parseVariableHeader(self):
		pass

	def parsePayloadHeader(self):
		pass		