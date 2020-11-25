#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import *


class PubackPacket(MQTTPacket):
	def parseVariableHeader(self)->None:
		variableHeader = self.data[self.fixed_size:]
		
		packetIdentifierMSB, packetIdentifierLSB=struct.unpack("!2B",variableHeader[:2])
		self.variable['packetIdentifier']=(packetIdentifierMSB<<8)+packetIdentifierLSB
		variableHeader=variableHeader[2:]
		
		self.variable['pubackReasonCode']=struct.unpack("!B",variableHeader[:1])
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
			if properties[i]==0x1F:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				if 'reasonString' not in self.variable['properties'].keys():	
					self.variable['properties']['reasonString'] = str1
				else:
					raise MQTTError("Malformed Packet : responseTopic already exists")
				i += offset1
			if properties[i] == 0x26:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				offset2,str2=readCustomUTF8String(properties[i+1+offset1:])
				if str1 not in self.variable['properties']['userProperty'].keys():
					self.variable['properties']['userProperty'][str1] = [str2]
				else:
					self.variable['properties']['userProperty'][str1].append(str2)
				i += offset1+offset2
			i+=1

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

