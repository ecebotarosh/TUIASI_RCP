#!/usr/bin/env python3

from MQTTPacket import MQTTPacket
import struct
from aux import CustomUTF8, VariableByte, BinaryData

class ConnackPacket(MQTTPacket):
	def __init__(self, data):
		self.data=data
		self.fixed={}
		self.fixed_size=0
		self.variable={}
		self.variable_size=0
		self.payload={}
		self.payload_size=0

	@staticmethod
	def generatePacketData(ack_flags : bool, reason_code: int, properties:dict, payload:dict) -> bytes:
		data = b"\x90"
		props = b""
		if 'ReasonString' in properties.keys():
			props += b"\x1F"+CustomUTF8.encode(properties['ReasonString'])
		if 'UserProperty' in properties.keys():
			for key in properties['UserProperty'].keys():
				for value in properties['UserProperty'][key]:
					props+=b"\x26"+CustomUTF8.encode(key)+CustomUTF8.encode(value)
		payload_data = b""
		for key in payload.keys():
			payload_data += bytes(payload[key])
		propertyLength = VariableByte.encode(len(props))
		#len(propertyLength) pare stupid, dar e necesar
		#propertyLength e format ca variable Byte si face parte din continutul pachetului.
		remainingLength = VariableByte.encode(len(propertyLength)+len(props)+len(payload_data))
		data += remainingLength + propertyLength + props + payload_data
		return data