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
	def generatePacketData(packetID: int, reasonString:str, userProperties:dict, payload:list) -> bytes:
		fixed = b"\x90"
		#TODO : add remaining length
		
		variable = struct.pack("!H", packetID)
		props = b"\x1F"+CustomUTF8.encode(reasonString)
			
		for key in userProperties.keys():
			for value in userProperties[key]:
				props+=b"\x26"+CustomUTF8.encode(key)+CustomUTF8.encode(value)
		variable+=VariableByte.encode(len(props))+props

		remainingLength = VariableByte.encode(len(variable))
		fixed+=remainingLength

		payload_data = b""

		for response_reason_code in payload:
			payload_data += struct.pack("!B", response_reason_code)

		return fixed+variable+payload_data