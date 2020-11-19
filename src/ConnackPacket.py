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
	def generatePacketData(ack_flags : bool, reason_code: int, properties:dict) -> bytes:
		data = b"\x20"
		if ack_flags:
			flags = b"\x01"
		else:
			flags = b"\x00"
		rc = struct.pack("!B", reason_code)
		props = b""
		if 'SessionExpiryInterval' in properties.keys():
			props += b"\x11"+struct.pack("!I", properties['SessionExpiryInterval'])
		if 'ReceiveMaximum' in properties.keys():
			props += b"\x21"+struct.pack("!H", properties['ReceiveMaximum'])
		if 'MaximumQoS' in properties.keys():
			props += b"\x24"+struct.pack("!B", properties['MaximumQoS'])
		if 'RetainAvailable' in properties.keys():
			props += b"\x25"+struct.pack("!B", properties['RetainAvailable'])
		if 'MaximumPacketSize' in properties.keys():
			props += b"\x27"+struct.pack("!I". properties['MaximumPacketSize'])
		if 'AssignedClientId' in properties.keys():
			props += b"\x12"+CustomUTF8.encode(properties['AssignedClientId'])
		if 'TopicAliasMaximum' in properties.keys():
			props += b"\x22"+struct.pack("!H". properties['TopicAliasMaximum'])
		if 'ReasonString' in properties.keys():
			props += b"\x1F"+CustomUTF8.encode(properties['ReasonString'])
		if 'UserProperty' in properties.keys():
			for key in properties['UserProperty'].keys():
				for value in properties['UserProperty'][key]:
					props+=b"\x26"+CustomUTF8.encode(key)+CustomUTF8.encode(value)
		if 'WildcardSubscriptionAvailable' in properties.keys():
			props += b"\x28"+struct.pack("!B", properties['WildcardSubscriptionAvailable'])
		if 'SubscriptionIdentifiersAvailable' in properties.keys():
			props += b"\x29"+struct.pack("!B", properties['SubscriptionIdentifiersAvailable'])
		if 'SharedSubscriptionAvailable' in properties.keys():
			props += b"\x2A"+struct.pack("!B", properties['SharedSubscriptionAvailable'])
		if 'ServerKeepAlive' in properties.keys():
			props += b"\x13"+struct.pack("!H", properties['ServerKeepAlive'])
		if 'ResponseInformation' in properties.keys():
			props += b"\x1A"+CustomUTF8.encode(properties['ResponseInformation'])
		if 'ServerReference' in properties.keys():
			props += b"\x1C"+CustomUTF8.encode(properties['ServerReference'])
		if 'AuthenticationMethod' in properties.keys():
			props += b"\x15"+CustomUTF8.encode(properties['AuthenticationMethod'])
		if 'AuthenticationData' in properties.keys():
			props += b"\x16"+BinaryData.fromBytesToBinary(properties['AuthenticationData'])
	
		propertyLength = VariableByte.encode(len(props))
		remainingLength = VariableByte.encode(2+len(propertyLength)+len(props))
		data += remainingLength + flags + rc + propertyLength + props
		return data