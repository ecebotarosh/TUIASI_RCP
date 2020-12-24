#!/usr/bin/env python3

from MQTTPacket import MQTTPacket
import struct
from aux import CustomUTF8, VariableByte, BinaryData

class SubackPacket(MQTTPacket):
	def __init__(self, data):
		self.data=data
		self.fixed={}
		self.fixed_size=0
		self.variable={}
		self.variable_size=0
		self.payload={}
		self.payload_size=0

	@staticmethod
	def generatePacketData(packetID: int, properties:dict, payload:list) -> bytes:
		fixed = b"\x90"
		#TODO : add remaining length
		
		variable = struct.pack("!H", packetID)
		props = b""
		myProperties = properties.keys()
		if 'ReasonString' in myProperties:
			props += b"\x1F"+CustomUTF8.encode(properties['ReasonString'])
			myProperties.remove('ReasonString')
		if 'UserProperty' in myProperties:
			for key in properties['UserProperty'].keys():
				for value in properties['UserProperty'][key]:
					props+=b"\x26"+CustomUTF8.encode(key)+CustomUTF8.encode(value)
			myProperties.remove('UserProperty')
		variable+=VariableByte.encode(len(props))+props

		remainingLength = VariableByte.encode(len(variable))
		fixed+=remainingLength

		payload_data = b""

		for response_reason_code in payload:
			payload_data += struct.pack("!B", response_reason_code)

		return fixed+variable+payload_data