#!/usr/bin/env python3

class MQTTPacket:
	def __init__(self, data):
		self.data=data
		self.fixed=b""
		self.variable=b""
		self.payload=b""

	def parseFixedHeader(self):
		pass

	def parseVariableHeader(self):
		pass

	def parsePayloadHeader(self):
		pass		