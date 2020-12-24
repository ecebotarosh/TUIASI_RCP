#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import *


class PubackPacket(MQTTPacket):
	def parseVariableHeader(self)->None:
		variableHeader = self.data[self.fixed_size:]
		
		self.variable['packetIdentifier']=struct.unpack("!H",variableHeader[:2])[0]
		
		variableHeader=variableHeader[2:]
		
		self.variable['pubackReasonCode']=struct.unpack("!B",variableHeader[:1])[0]
		variableHeader=variableHeader[1:]

		properties=self.data[self.fixed_size+3:]
		num=b""
		for byte in properties:
			num+=struct.pack("!B",byte)
			if byte<0x80:
				break
		required=len(num)
		
		self.variable['propertyLength']=struct.unpack("!{}s".format(required),num)[0]
		self.variable['propertyLength']=VariableByte.decode(self.variable['propertyLength'])
		self.variable['properties']={}
		self.variable['properties']['userProperty']={}
		self.variable_size=self.variable['propertyLength']+3
		properties=properties[required:]

		i = 0
		while i<self.variable['propertyLength']:
			if properties[i] == 0x1F:
				reason_string_offset, self.variable['reasonString'] = readCustomUTF8String(payloadHeader[i+1:])
				i += reason_string_offset
			elif properties[i] == 0x26:
				offset1, str1 = readCustomUTF8String(payloadHeader[i+1:])
				offset2, str2 = readCustomUTF8String(payloadHeader[i+1+offset1:])
				if str1 not in self.payload['willProperties']['userProperty'].keys():
					self.payload['willProperties']['userProperty'][str1] = [str2]
				else:
					self.payload['willProperties']['userProperty'][str1].append(str2)
				i += offset1+offset2
			i+=1

	@staticmethod
	def generatePacketData(packetId : str, reason_code: int, properties:dict) -> bytes:
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
		#1 pentru flags si 1 pentru rc
		remainingLength = VariableByte.encode(2+len(propertyLength)+len(props))
		#len(propertyLength) pare stupid, dar e necesar
		#propertyLength e format ca variable Byte si face parte din continutul pachetului.
		data += remainingLength + flags + rc + propertyLength + props
		return data

if __name__=="__main__":
	#fixed header
	fixed=b"\x40"

	packetId=b"\x00\x10"
	puback_reason_code=b"\xff"
	reason_string=b"\x1f"+CustomUTF8.encode("./reason_string1/")
	userProperty=b"\x26"+CustomUTF8.encode("user1")+CustomUTF8.encode("utilizeaza dev")+b"\x26"+CustomUTF8.encode("user2")+CustomUTF8.encode("add commit")
	properties=reason_string+userProperty
	property_length=VariableByte.encode(len(properties))
	variableHeader=packetId+puback_reason_code+property_length+properties

	len_variable_header=len(variableHeader)
	remainingLength=VariableByte.encode(len_variable_header)

	data=fixed+remainingLength+variableHeader
	data=struct.pack("!{}s".format(len(data)),data)
	packet=PubackPacket(data)
	packet.parseFixedHeader()
	packet.parseVariableHeader()
	print(packet.fixed)
	print(packet.variable)

