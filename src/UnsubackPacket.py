#!/usr/bin/env python3

import struct
import sys
from MQTTPacket import MQTTPacket
from aux import *

class UnsubackPacket(MQTTPacket):
	def parseVariableHeader(self)->None:
		variableHeader = self.data[self.fixed_size:]
		
		packetIdentifierMSB, packetIdentifierLSB=struct.unpack("!2B",variableHeader[:2])
		self.variable['packetIdentifier']=(packetIdentifierMSB<<8)+packetIdentifierLSB
		variableHeader=variableHeader[2:]

		properties=self.data[self.fixed_size+2:]
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
		self.variable_size=self.variable['propertyLength']+2
		properties=properties[required:]

		i = 0
		while i<self.variable['propertyLength']:
			if properties[i]==0x1F:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				if 'reasonString' not in self.variable['properties'].keys():	
					self.variable['properties']['reasonString'] = str1
				else:
					raise MQTTError("Malformed Packet : reasonString already exists")
				i += offset1
			# if properties[i]==0x1F:
			# 	offset1,str1=readCustomUTF8String(properties[i+1:])
			# 	self.variable['properties']['reasonCode'].append(str1)
			# 	i+=offset1
			
			if properties[i] == 0x26:
				offset1,str1=readCustomUTF8String(properties[i+1:])
				offset2,str2=readCustomUTF8String(properties[i+1+offset1:])
				if str1 not in self.variable['properties']['userProperty'].keys():
					self.variable['properties']['userProperty'][str1] = [str2]
				else:
					self.variable['properties']['userProperty'][str1].append(str2)
				i += offset1+offset2
			i+=1

	def parsePayloadHeader(self):
		offset = self.fixed_size+self.variable_size+1
		self.payload_size = self.fixed['remainingLength']-self.variable_size
		payloadHeader = self.data[offset:]
		self.payload = {'reasonCode':[]}
		while len(payloadHeader)>0:
			data=struct.unpack("!B",payloadHeader[:1])[0]
			self.payload['reasonCode'].append(data)
			payloadHeader=payloadHeader[1:]

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

			
if __name__=="__main__":
	
	fixed=b"\xb0"
	packetId=b"\x00\x11"

	reason_string=b"\x1f"+CustomUTF8.encode("reasonString:::data")
	userProperty=b"\x26"+CustomUTF8.encode("user1")+CustomUTF8.encode("checkout main")+b"\x26"+CustomUTF8.encode("user2")+CustomUTF8.encode("add commit")
	properties=reason_string+userProperty

	property_length=VariableByte.encode(len(properties))
	variableHeader=packetId+property_length+properties
	len_var_header=len(variableHeader)
	remainigLength=VariableByte.encode(len_var_header)
	reason_code=b"\x00\x10"
	data=fixed+remainigLength+variableHeader+reason_code
	data=struct.pack("!{}s".format(len(data)),data)

	packet=UnsubackPacket(data)
	packet.parseFixedHeader()
	packet.parseVariableHeader()
	packet.parsePayloadHeader()
	print(packet.fixed)
	print(packet.variable)
	print(packet.payload)


	customData = UnsubackPacket.generatePacketData(17, "reasonString:::data", {"user1":["checkout main"], "user2":["add commit"]}, [0, 16])
	customPacket = UnsubackPacket(customData)
	customPacket.parseFixedHeader()
	customPacket.parseVariableHeader()
	customPacket.parsePayloadHeader()
	print(customPacket.fixed)
	print(customPacket.variable)
	print(customPacket.payload)